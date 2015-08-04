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
InputFilenames(cl::Positional, //vllt auch cl::OneOrMore und dann in jedem einfuegen
               cl::desc("<input bitcode files>"));

static cl::opt<std::string>
OutputFilename("o", cl::desc("LLVM Bitcode Output"), cl::init("-"),
               cl::value_desc("filename"));

static cl::list<std::string>
FnAttribute("attribute", cl::desc("Add an attribute value to a function"),
               cl::OneOrMore, cl::value_desc("function>,<attribute>=<attr-value"));

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


    //--------------
    // Iterate over every occurence of -attribute:
    for(auto concreteAttr : FnAttribute) {
        // Parse --attribute parameter:
        std::size_t oldPos = 0;
        std::size_t pos = concreteAttr.find(',',oldPos);
        if(pos == std::string::npos) {
            errs() << "Wrong attribute syntax: " << concreteAttr
                   << "\nHas to be: <function>,<attribute>=<attr-value>\n";
            return 1;
        }
        std::string functionName = concreteAttr.substr(oldPos, pos-oldPos);
    
        oldPos = pos+1;
        pos = concreteAttr.find('=',oldPos);
        if(pos == std::string::npos) {
            errs() << "Wrong attribute syntax: " << concreteAttr
                   << "\nHas to be: <function>,<attribute>=<attr-value>\n";
            return 1;
        }
        std::string attributeName= concreteAttr.substr(oldPos, pos-oldPos);
    
        oldPos = pos+1;
        if(oldPos >= concreteAttr.size()) {
            errs() << "Wrong attribute syntax: " << concreteAttr
                   << "\nHas to be: <function>,<attribute>=<attr-value>\n";
            return 1;
        }
        std::string attrVal = concreteAttr.substr(oldPos, std::string::npos);
        //--------------
    
        //--------------
        // adding Attribute/Value to LLVM Bitcode Output
        for (auto &function : *Composite) {
            if(function.getName().str() == functionName) {
                function.addFnAttr(attributeName, attrVal);
            }
        }
        //--------------
    }

    if (DumpAsm) errs() << "Here's the assembly:\n" << *Composite;

    std::string EC;
    tool_output_file Out(OutputFilename.c_str(), EC, sys::fs::F_None);
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
