//===- llvm-link.cpp - Low-level LLVM linker ------------------------------===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// This utility may be invoked in the following manner:
//  llvm-link a.bc b.bc c.bc -o x.bc
//
//===----------------------------------------------------------------------===//

#define llvm33 (LLVM_VERSION_MAJOR == 3 && LLVM_VERSION_MAJOR == 3)
#define llvm34 (LLVM_VERSION_MAJOR == 3 && LLVM_VERSION_MAJOR == 4)

#if __STDC_VERSION__ >= 201112L || __cplusplus >= 201103L
typedef struct {
	long long __clang_max_align_nonce1
	   __attribute__((__aligned__(__alignof__(long long))));
	long double __clang_max_align_nonce2
	__attribute__((__aligned__(__alignof__(long double))));
	} max_align_t;
#define __CLANG_MAX_ALIGN_T_DEFINED
#endif

//3.6 #include <llvm/Linker/Linker.h>
//3.6 #include <llvm/IR/Verifier.h>
//3.6 #include <llvm/IR/CFG.h>
#include <llvm/Support/CFG.h>
#include <llvm/Linker.h>
#include <llvm/Analysis/Verifier.h>

#include <llvm/Bitcode/ReaderWriter.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/IRBuilder.h>

#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/CommandLine.h>
#include <llvm/Support/ManagedStatic.h>
#include <llvm/Support/Path.h>
#include <llvm/Support/PrettyStackTrace.h>
#include <llvm/Support/Signals.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/SystemUtils.h>
#include <llvm/Support/ToolOutputFile.h>
#include <llvm/Support/FileSystem.h>
#include <llvm/Analysis/Interval.h>



#include <sstream>
#include <fstream>
#include <memory>
#include <list>
using namespace llvm;

static cl::list<std::string>
InputFilenames(cl::Positional, cl::OneOrMore,
               cl::desc("<input bitcode files>"));

static cl::list<std::string>
SystemCalls("s", cl::OneOrMore,
            cl::desc("<input bitcode files>"));


static cl::opt<std::string>
OutputFilename("o", cl::desc("LLVM Bitcode Output"), cl::init("-"),
               cl::value_desc("filename"));

static cl::opt<std::string>
StructureOutputFilename("O", cl::desc("Structure Output"),
                        cl::init(""),
                        cl::Required,
                        cl::value_desc("filename"));


static cl::opt<bool>
Force("f", cl::desc("Enable binary output on terminals"));

static cl::opt<bool>
OutputAssembly("S",
               cl::desc("Write output as LLVM assembly"), cl::Hidden);

static cl::opt<bool>
Verbose("v", cl::desc("Print information about actions taken"));

static cl::opt<bool>
DumpAsm("d", cl::desc("Print assembly as linked"), cl::Hidden);

// LoadFile - Read the specified bitcode file in and return it.  This routine
// searches the link path for the specified file to try to find it...
//
static inline std::unique_ptr<Module> LoadFile(const char *argv0, const std::string &FN,
                                               LLVMContext& Context) {
    SMDiagnostic Err;
    if (Verbose) errs() << "Loading '" << FN << "'\n";
	    //3.6 std::unique_ptr<Module> Result = 0;
	//3.6 Result = parseIRFile(FN, Err, Context);
    Module* Result = 0;

    Result = ParseIRFile(FN, Err, Context);
    if (Result) return std::unique_ptr<Module>(Result);   // Load successful!

    Err.print(argv0, errs());
    return NULL;
}

unsigned split_counter = 0;
static inline void SplitBasicBlocks(Module &module) {
    for (auto &function : module) {
        std::list<BasicBlock *> bbs;
        for (BasicBlock &_bb : function) {
            bbs.push_back(&_bb);
        }
        for (BasicBlock *bb : bbs) {
            BasicBlock::iterator it = bb->begin();
            while (it != bb->end()) {
                while (isa<InvokeInst>(*it) || isa<CallInst>(*it)) {
                    std::stringstream ss;
                    ss << "BB" << split_counter++;
                    bb = bb->splitBasicBlock(it, ss.str());
                    it = bb->begin();
                    ++it;

                    if (isa<InvokeInst>(*it) || isa<CallInst>(*it))
                        continue;

                    ss.str("");
                    ss << "BB" << split_counter++;
                    bb = bb->splitBasicBlock(it, ss.str());
                    it = bb->begin();
                }
                ++it;
            }
        }
    }
}

static inline void AddKickoffFunctionCalls(Module & module) {
    std::vector<Type *> args;
    FunctionType *kickoff_type = FunctionType::get(Type::getVoidTy(getGlobalContext()), args, false);
    unsigned task_count = 0;
    for (auto &function : module) {
        BasicBlock &bb = *function.begin();
        IRBuilder<> Builder(getGlobalContext());
        if (function.getName().startswith("OSEKOS_TASK_FUNC")) {
			Instruction *inst = &*bb.begin();
			Builder.SetInsertPoint(inst);

            std::stringstream ss;
            ss << "OSEKOS_kickoff_" << task_count++;
            Function *F = Function::Create(kickoff_type,
                                           Function::ExternalLinkage,
                                           ss.str(), &module);
            std::vector<Value*> ArgsV;
            Builder.CreateCall(F, ArgsV);

            // Split after Call
            BasicBlock::iterator it = bb.begin();
            ss.str("");
            ss << "BB" << split_counter++;
            bb.splitBasicBlock(++it, ss.str());
        }
    }
}

static inline void RenameSystemcall(Module &module, CallInst * call) {
    Function * func = call->getCalledFunction();
    FunctionType *func_ty = func->getFunctionType();

    std::stringstream name;
    name << func->getName().str() << "_" << call->getParent()->getName().str();

    Function *x = Function::Create(func_ty,
                                   Function::ExternalLinkage,
                                   name.str(), &module);
    call->setCalledFunction(x);
}

static inline void RenameSystemcalls(Module &module) {
    for (auto &function : module) {
        for (auto &bb : function) {
            for (auto &inst : bb) {
                if (CallInst* callInst = dyn_cast<CallInst>(&inst)) {
                    Function * func = callInst->getCalledFunction();
                    if (!func) continue;
                    // Found a Call. Is it a systemcall?
                    for (auto syscall : SystemCalls) {
                        if (func->getName() == syscall) {
                            RenameSystemcall(module, callInst);
                            break;
                        }
                    }
                }
            }
        }
    }
}


static inline void DumpArgument(std::ofstream &out, Value *arg) {
    if (LoadInst *load = dyn_cast<LoadInst>(arg)) {
        if (GlobalVariable *arg0 = dyn_cast<GlobalVariable>(load->getOperand(0))) {
            out << "\"" << arg0->getName().str() << "\"";
            return;
        }
    } else if (ConstantInt * CI = dyn_cast<ConstantInt>(arg)) {
        out << CI->getSExtValue();
        return;
    } else if (BinaryOperator *binop = dyn_cast<BinaryOperator>(arg)) {
        if (binop->getOpcode() == Instruction::BinaryOps::Or) {
            out << "(";
            DumpArgument(out, binop->getOperand(0));
            out << ", ";
            DumpArgument(out, binop->getOperand(1));
            out << ")";
            return;
        }
    }

    out << "None";
}

static inline void DumpModuleStructure(Module &module) {
    std::ofstream out(StructureOutputFilename);
    for (auto &function : module) {
        // Only non-empty functions
        for (auto &bb : function) {
            // Name all basic blocks
            if (!bb.getName().startswith("BB")) {
                std::stringstream ss;
                ss << "BB" << split_counter++;
                bb.setName(ss.str());
            }
        }
    }

    out << "{\n";
    for (auto &function : module) {
        // Only non-empty functions
        if (function.begin() != function.end()) {
            out << "  \"" << function.getName().str() << "\": {\n";
            out << "    \"entry\": \"" << function.getEntryBlock().getName().str() << "\",\n";
            for (auto &bb : function) {
                out << "    \"" << bb.getName().str() << "\": {\n";
                // Print all successors
                out << "       \"successors\": [";
                for (auto it = succ_begin(&bb); it != succ_end(&bb); ++it){
                    BasicBlock *Succ = *it;
                    out << "\"" << Succ->getName().str() << "\", ";
                }
                out << "],\n";
                bool call_found = false;
                for (auto &inst : bb) {
                    if (isa<CallInst>(inst)) {
                        CallInst *call = (CallInst *)&inst;
                        Function * func = call->getCalledFunction();
                        if (func) {
                            assert(call_found == false);
                            call_found = true;
                            out << "        \"call\": \"" << func->getName().str() << "\",\n";
                            out << "        \"arguments\": [";
                            for (unsigned i = 0; i < call->getNumArgOperands(); ++i) {
                                Value *arg = call->getArgOperand(i);
                                DumpArgument(out, arg);
                                out << ", ";
                            }
                            out << "],\n";
                        }
                    } else if (InvokeInst *invoke = dyn_cast<InvokeInst>(&inst)) {
                        Function * func = invoke->getCalledFunction();
                        if (func) {
                            assert(call_found == false);
                            call_found = true;
                            out << "        \"call\": \"" << func->getName().str() << "\",\n";
                            out << "        \"arguments\": [";
                            for (unsigned i = 0; i < invoke->getNumArgOperands(); ++i) {
                                Value *arg = invoke->getArgOperand(i);
                                DumpArgument(out, arg);
                                out << ", ";
                            }
                            out << "],\n";
                        }
                    }

                }
                out << "    },\n";
            }
            out << "  },\n";
        }
    }
    out << "}\n";
}

static inline void TransformModule(Module &module) {
    SplitBasicBlocks(module);
    AddKickoffFunctionCalls(module);
    RenameSystemcalls(module);
    DumpModuleStructure(module);
}

int main(int argc, char **argv) {
    // Print a stack trace if we signal out.
    sys::PrintStackTraceOnErrorSignal();
    PrettyStackTraceProgram X(argc, argv);

    LLVMContext &Context = getGlobalContext();
    llvm_shutdown_obj Y;  // Call llvm_shutdown() on exit.
    cl::ParseCommandLineOptions(argc, argv, "llvm dosek extractor\n");

    unsigned BaseArg = 0;
    std::string ErrorMessage;

    auto Composite = LoadFile(argv[0], InputFilenames[BaseArg], Context);
    if (Composite.get() == 0) {
        errs() << argv[0] << ": error loading file '"
               << InputFilenames[BaseArg] << "'\n";
        return 1;
    }

    Linker L(Composite.get());
    for (unsigned i = BaseArg+1; i < InputFilenames.size(); ++i) {
        auto M = LoadFile(argv[0], InputFilenames[i], Context);
        if (M.get() == 0) {
            errs() << argv[0] << ": error loading file '" <<InputFilenames[i]<< "'\n";
            return 1;
        }

        if (Verbose) errs() << "Linking in '" << InputFilenames[i] << "'\n";

		std::string ErrorMessage;
        if (L.linkInModule(M.get(), &ErrorMessage)) {
            errs() << argv[0] << ": link error in '" << InputFilenames[i]
                   << "': " << ErrorMessage << "\n";
            return 1;
        }
    }

    if (StructureOutputFilename == "") {
        errs() << "No structure outputfile given\n";
        return 1;
    }

    //---- SNIP ----
    // Here, we add our custom extractor
    TransformModule(*Composite);
    //--------------

    if (DumpAsm) errs() << "Here's the assembly:\n" << *Composite;

    std::string EC;
#if llvm33
	tool_output_file Out(OutputFilename.c_str(), EC,
						 raw_fd_ostream::F_Binary);
#elif llvm34
    tool_output_file Out(OutputFilename.c_str(), EC, sys::fs::F_None);
#endif
    if (EC != "") {
        errs() << EC << '\n';
        return 1;
    }

    if (verifyModule(*Composite)) {
        errs() << argv[0] << ": linked module is broken!\n";
        return 1;
    }

    if (Verbose) errs() << "Writing bitcode...\n";
    if (OutputAssembly) {
        Out.os() << *Composite;
    } else if (Force || !CheckBitcodeOutputToConsole(Out.os(), true))
        WriteBitcodeToFile(Composite.get(), Out.os());

    // Declare success.
    Out.keep();

    return 0;
}
