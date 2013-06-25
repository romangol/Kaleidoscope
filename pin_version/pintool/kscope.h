#ifndef _KSCOPE_H_
#define _KSCOPE_H_

#include "pin.H"

struct MemOP
{
	UINT32 uid;
	VOID * addr;
	UINT32 content;
	unsigned char type;
	unsigned char len;
	unsigned short tid;
};

struct RegS
{
	ADDRINT ip;
	THREADID id;
	ADDRINT eax;
	ADDRINT ebx;
	ADDRINT ecx;
	ADDRINT edx;
	ADDRINT edi;
	ADDRINT esi;
	ADDRINT ebp;
	ADDRINT esp;
	unsigned int uid;
};


int kaleidoscope( int argc, char * argv[] );
int profiler( int argc, char * argv[] );
int call_trace( int argc, char * argv[] );
int entropy( int argc, char * argv[] );

#endif
