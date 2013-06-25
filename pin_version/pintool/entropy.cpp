#include <iostream>
#include <fstream>
#include <set>
#include "pin.H"
#include "kscope.h"

/*
 * The lock for I/O.
 */
static PIN_LOCK fileLock;


static FILE * memTrace;

static ADDRINT StartAddr = 0xFFFFFFFF;
static ADDRINT EndAddr = 0xFFFFFFFF;
static ADDRINT AddrUpBound = 0x01000000;

static bool RecordFlag = false;

static ADDRINT WIP = 0;
static VOID * WAddr = 0;

using std::set;
static set<ADDRINT> HotMem;

// Record a memory read record
VOID mem_read( ADDRINT ip, VOID * addr, UINT32 len )
{
	GetLock(&fileLock, 1);
	if ( len == 1 )
		fprintf( memTrace, "R%d|%08x:[%08x]=%02x\n", len, ip, addr, static_cast<UINT8*>(addr)[0] );
	else if ( len == 2 )
		fprintf( memTrace, "R%d|%08x:[%08x]=%04x\n", len, ip, addr, static_cast<UINT16*>(addr)[0] );
	else
		fprintf( memTrace, "R%d|%08x:[%08x]=%08x\n", len, ip, addr, static_cast<UINT32*>(addr)[0] );
	ReleaseLock(&fileLock);
}

// Record a memory write record
VOID mem_write( ADDRINT ip, VOID * addr, UINT32 len )
{
	GetLock(&fileLock, 1);
	WIP = ip;
	WAddr = addr;
	fprintf( memTrace, "W%d|%08x:[%08x]=?\n", len, ip, addr );
	ReleaseLock(&fileLock);
}

VOID mem_write_content( UINT32 len )
{
	GetLock(&fileLock, 1);
	if ( len == 1 )
		fprintf( memTrace, "W%d|%08x:[%08x]=%02x\n", len, WIP, WAddr, static_cast<UINT8*>(WAddr)[0] );
	else if ( len == 2 )
		fprintf( memTrace, "W%d|%08x:[%08x]=%04x\n", len, WIP, WAddr, static_cast<UINT16*>(WAddr)[0] );
	else
		fprintf( memTrace, "W%d|%08x:[%08x]=%08x\n", len, WIP, WAddr, static_cast<UINT32*>(WAddr)[0] );
	ReleaseLock(&fileLock);
}



static VOID insert_mem_trace(INS ins)
{
    if (INS_IsMemoryWrite(ins))
    {
		INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_write), IARG_INST_PTR, IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_END);

		if (INS_HasFallThrough(ins))
            INS_InsertPredicatedCall(ins, IPOINT_AFTER, AFUNPTR(mem_write_content), IARG_MEMORYWRITE_SIZE, IARG_END);
        if (INS_IsBranchOrCall(ins))
            INS_InsertPredicatedCall(ins, IPOINT_TAKEN_BRANCH, AFUNPTR(mem_write_content), IARG_MEMORYWRITE_SIZE, IARG_END);
    }
	
    if ( INS_HasMemoryRead2(ins) )
        INS_InsertPredicatedCall(ins, IPOINT_BEFORE, AFUNPTR(mem_read), IARG_INST_PTR, IARG_MEMORYREAD2_EA, IARG_MEMORYREAD_SIZE, IARG_END);

	if ( INS_IsMemoryRead(ins) )
		INS_InsertPredicatedCall(ins, IPOINT_BEFORE, AFUNPTR(mem_read), IARG_INST_PTR, IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_END);

}


// Pin calls this function every time a new instruction is encountered
VOID Inst_Entropy(INS ins, VOID *v)
{
	ADDRINT pc = INS_Address (ins);
	if ( HotMem.find(pc) != HotMem.end() )
		insert_mem_trace(ins);
}


// This function is called when the application exits
static VOID Fini_Entropy(INT32 code, VOID *v)
{
    fclose( memTrace );
	
	puts("--FINI--\n");
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

static INT32 Usage()
{
    PIN_ERROR("This Pintool prints the IPs of every instruction executed\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}

static bool init_config()
{
	memTrace = fopen("data/entropy.log", "w");

	// init HotMem
	std::ifstream ifs( "config/hotmem.cfg" );
	
	std::string s;
    while( ifs )
    {
		std::getline( ifs, s );
		ADDRINT i;
		sscanf( s.c_str(), "%08x\n", &i );
		HotMem.insert(i);
    }

	return ( NULL != memTrace );
}

int entropy(int argc, char * argv[])
{
    // Initialize pin
    if ( PIN_Init(argc, argv) )
		return Usage();

	if ( !init_config() )
	{
		puts("Init record file fails\n");
		return -1;
	}

	// Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(Inst_Entropy, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini_Entropy, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
