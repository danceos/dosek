#!/usr/bin/env Rscript
library(RMySQL)
library(ggplot2)

# variant and benchmarks from args
args <- commandArgs(TRUE)
variants <- args[1]
benchmarks <- args[-1]

# connect to DB using $HOME/my.cnf
m <- dbDriver("MySQL")
con <- dbConnect(m)

# prepare view
view_sql <- "view.sql"
stopifnot(file.exists(view_sql))
sql <- readChar(view_sql, nchar = file.info(view_sql)$size)
sql <- gsub("\\s", " ", sql)
queries <- head(unlist(strsplit(sql,";")),-1)
for(sql in queries) {
	dbSendQuery(con, sql)
}

# for each benchmark
for(variant in variants) {
for(benchmark in benchmarks) {
print(paste(variant, benchmark))

# fetch all occurrences for variant
sql <- sprintf("select * from occurences where variant='%s' and benchmark like '%s%%'", variant, benchmark)
fail <- dbGetQuery(con, sql)

# remove known_outcomes
fail <- subset(fail, known_outcome == FALSE)

# remove ROM accesses
fail <- fail[!(fail$data_address %in% 0x100000:0x1fffff),]

# extract benchmark type
fail$type[grepl("-ip-?", fail$benchmark)] <- "ip"
fail$type[grepl("-regs-?", fail$benchmark)] <- "regs"
fail$type[grepl("-mem-?", fail$benchmark)] <- "mem"
fail$type <- factor(fail$type)

# turn some fields to factors
fail$variant <- factor(fail$variant)
fail$benchmark <- factor(fail$benchmark)
fail$resulttype <- factor(fail$resulttype)

# extract encoded option
fail$encoded <- !grepl("-unencoded-?", fail$benchmark)
fail$fencoded <- factor(c("unencoded", "encoded")[fail$encoded + 1])

# extract MPU option
fail$mpu <- !grepl("-nompu-?", fail$benchmark)
fail$fmpu <- factor(c("nompu", "mpu")[fail$mpu + 1])

# name options
fail$opts <- factor( paste( fail$fencoded, fail$fmpu ))

# hex format helper
hex <- function(x) {
	lo <- as.integer(as.numeric(x) %% 2**16)
	hi <- as.integer(as.numeric(x) / 2**16)
	ifelse(hi>0, 
		sprintf("%x%.4x", hi, lo),
		sprintf("%x", lo)
	)
}

# group addresses modulo 4
fail$data_address4 <- floor(fail$data_address/4)*4

# grouped, named data addresses
fail$data_group <- hex(fail$data_address4)

fail$data_group[fail$data_group=="0"]="%eax"
fail$data_group[fail$data_group=="10"]="%ecx"
fail$data_group[fail$data_group=="20"]="%edx"
fail$data_group[fail$data_group=="30"]="%ebx"
fail$data_group[fail$data_group=="40"]="SP"
fail$data_group[fail$data_group=="50"]="%ebp"
fail$data_group[fail$data_group=="60"]="%esi"
fail$data_group[fail$data_group=="70"]="%edi"
fail$data_group[fail$data_group=="80"]="IP"
fail$data_group[fail$data_group=="90"]="EFLAGS"
fail$data_group[fail$data_group=="a0"]="%cs"
fail$data_group[fail$data_group=="b0"]="%ds"
fail$data_group[fail$data_group=="c0"]="%es"
fail$data_group[fail$data_group=="d0"]="%fs"
fail$data_group[fail$data_group=="e0"]="%gs"
fail$data_group[fail$data_group=="f0"]="%ss"
fail$data_group[fail$data_group=="100"]="%cr0"
fail$data_group[fail$data_group=="110"]="%cr1"
fail$data_group[fail$data_group=="120"]="%cr2"
fail$data_group[fail$data_group=="130"]="%cr3"
fail$data_group[fail$data_group=="140"]="%cr4"

fail$data_group[fail$data_address4 == 0xfee00080]="LAPIC.TPR"
fail$data_group[fail$data_address %in% 0x201000:0x201fff]="os_stack"

# read objdump files
for(enc in levels(fail$fencoded)) {
	for(mpu in levels(fail$fmpu)) {
		objfile <- paste(variant, "-", benchmark, "-", enc, "-", mpu, ".syms", sep="")
		cols <- c(8,-1,7,-1,5,-1,8,-1,500)
		colnames <- c("addr", "flags", "section", "size", "symbol")
		if(file.exists(objfile)) {
			t <- read.fwf(objfile, cols, header=FALSE, skip=4, col.names=colnames, colClasses="character")
			t <- t[complete.cases(t),]
			t$addr <- as.integer(paste("0x", t$addr, sep=""))
			t$size <- as.integer(paste("0x", t$size, sep=""))
			t$name <- sapply(strsplit(t$symbol, "::"), function(x) tail(x,1))
			realsyms <- subset(t, size>0)
			for(i in 1:nrow(realsyms)) {
				sym <- realsyms[i,]
				fail$data_group[fail$data_address %in% seq(sym$addr, sym$addr+sym$size) & fail$fencoded == enc & fail$fmpu == mpu] = sym$name
			}
		} else {
			print(paste(objfile, "not found, not importing symbol names"))
		}
	}
}

# order data_group by type and address
fail$data_group <- factor(fail$data_group, levels=unique(fail$data_group[order(fail$type, fail$data_address4, decreasing=TRUE)]), ordered=TRUE)

# SDC results
sdc <- subset(fail, fail$resulttype == "ERR_WRONG_RESULT")

# extract invalid tracepoint information
r <- regexec("(.+)@ IP (0x.+) \\(checkpoint (.+)\\)", sdc$details)
m <- regmatches(sdc$details, r)
sdc$trace <- as.integer(sapply(m, function(x) x[4]))
sdc$trace_ip <- as.numeric(sapply(m, function(x) x[3]))
sdc$trace_err <- sapply(m, function(x) x[2])


# plot base
base_plot <- ggplot(sdc) +
	labs(title = paste(variant, benchmark)) +
	guides(fill = guide_legend("trace")) +
	ylab("SDC occurrences") + 
	xlab("injection address")

# full MPU~encoded grid
data_grid <- base_plot + 
	geom_bar(aes(x=data_group, y=occurrences, group=factor(trace), fill=factor(trace)), stat="summary", fun.y="sum") +
	facet_grid(fencoded ~ fmpu) +
	coord_flip()

# MPU~encoded variants in a row
data_row <- base_plot + 
	geom_bar(aes(x=data_group, y=occurrences, group=factor(trace), fill=factor(trace)), stat="summary", fun.y="sum") +
	facet_grid(opts ~ .) +
	coord_flip()

# MPU~encoded variants as dodged bars
data_dodge <- base_plot +
	geom_bar(aes(x=data_group, y=occurrences, group=opts, fill=opts), stat="summary", fun.y="sum", position="dodge") +
	theme(legend.position = "bottom") +
	coord_flip() +
	guides(fill = guide_legend("variant"))

# totals by variant/type
data_total <- base_plot +
	geom_bar(aes(x=opts, y=occurrences, fill=type), stat="summary", fun.y="sum") +
	guides(fill = guide_legend("type")) +
	xlab("variant")

# occs by resulttype
result_types <- ggplot(fail) +
	geom_bar(aes(x=resulttype, y=occurrences, fill=opts), stat="summary", fun.y="sum",position="dodge") +
	guides(fill = guide_legend("variant")) +
	labs(title = paste(variant, benchmark)) +
	xlab("result type")

# occs by stack_os address
os_stack <- ggplot(subset(sdc,data_group=="os_stack")) +
	geom_bar(aes(width=.9, x=data_address+.5, y=occurrences, group=factor(trace), fill=factor(trace)), stat="summary", fun.y="sum") +
	facet_grid(opts ~ .) +
	scale_x_continuous(label=hex, breaks=seq(0x201000, 0x202000, 16), minor_breaks=seq(0x201000, 0x202000, 4)) +
	labs(title = paste(variant, benchmark)) +
	guides(fill = guide_legend("trace")) +
	ylab("SDC occurrences") + 
	xlab("injection stack address")


if(FALSE){ # TESTING
# sdc in os_stack by instr
ggplot(subset(sdc,data_group=="stack_os"))+geom_bar(aes(width=.9,x=factor(injection_instr),  y=occurrences, group=factor(trace), fill=factor(trace)), stat="summary", fun.y="sum")+facet_grid(encoded ~ mpu, labeller=label_both) + scale_x_discrete(label=hex)+coord_flip()

# occs by instr
ggplot(subset(sdc,type!="ip"), aes(x=injection_instr,y=occurrences))+geom_bar( stat="summary", fun.y="sum",position="dodge")+facet_grid(mpu~encoded,labeller=label_both,scales="free")

# instr vs data vs variant
ggplot(subset(sdc,type!="ip"), aes(x=factor(injection_instr),y=factor(data_group),size=occurrences,alpha=occurrences,color=factor(opts)))+geom_point()+facet_grid(mpu~encoded,labeller=label_both,scales="free")

# rel instr vs data
ggplot(subset(sdc,type!="ip"), aes(x=relative_instruction,y=factor(data_group),size=occurrences,alpha=occurrences,color=factor(opts)))+geom_point()+facet_grid(mpu~encoded,labeller=label_both,scales="free")

# instruction vs rel instruction
ggplot(subset(sdc,relative_instruction>100), aes(x=relative_instruction,y=injection_instr,size=occurrences,alpha=occurrences,color=factor(opts)))+geom_point()+scale_y_continuous(labels=hex,breaks=seq(0x100000,0x112000,0x2000))+facet_grid(mpu~encoded,labeller=label_both,scales="free")
ggplot(sdc, aes(x=relative_instruction,y=injection_instr,size=occurrences,alpha=occurrences,color=factor(opts)))+geom_point()+facet_grid(mpu~encoded,labeller=label_both,scales="free")+scale_y_continuous(labels=hex,breaks=seq(0x100000,0x112000,0x2000))

# invalid tracepoint detection offset
ggplot(sdc, aes(x=factor(type),fill=factor(trace-experiment_number),y=occurrences))+geom_bar(stat="summary",fun.y="sum",position="dodge")+facet_grid(mpu~encoded,labeller=label_both)
ggplot(sdc, aes(x=factor(trace-experiment_number),fill=factor(type),y=occurrences))+geom_bar(stat="summary",fun.y="sum",position="dodge")+facet_grid(mpu~encoded,labeller=label_both)
ggplot(sdc, aes(x=1,fill=factor(type),y=occurrences))+geom_bar(stat="summary",fun.y=sum)+facet_grid(trace~experiment_number,margins=TRUE,labeller=label_both)

} #END TESTING

# save data to file
save(fail, file=paste("fail-", variant, "-", benchmark ,".Rdata", sep=""))

# save all plots to PDF
pdf(paste("fail-", variant, "-", benchmark ,".pdf", sep=""), paper="a4r", title=paste(variant, benchmark), width=11 , height=8)

plot(result_types, newpage=TRUE)
plot(data_total, newpage=TRUE)
plot(data_grid, newpage=TRUE)
plot(data_row, newpage=TRUE)
plot(data_dodge, newpage=TRUE)
plot(os_stack, newpage=TRUE)

dev.off()

} # for benchmark
} # for variant

dbDisconnect(con)
