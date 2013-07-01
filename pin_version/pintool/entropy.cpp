#include <iostream>
#include <fstream>
#include <set>
#include <map>
#include <math.h>
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
using std::map;

static set<ADDRINT> HotMem;

struct Slot
{
	unsigned int d[256];
};

static map<ADDRINT, Slot> ReadEntropySlot;
static map<ADDRINT, Slot> WriteEntropySlot;

// Record a memory read record
VOID mem_read( ADDRINT ip, VOID * addr, UINT32 len )
{
	if ( len == 1 )
	{
		++ReadEntropySlot[ip].d[ static_cast<UINT8*>(addr)[0] ];
	}
	else if ( len == 2 )
	{
		++ReadEntropySlot[ip].d[ static_cast<UINT8*>(addr)[0] ];
		++ReadEntropySlot[ip].d[ static_cast<UINT8*>(addr)[1] ];
	}
	else if ( len == 4 )
	{
		++ReadEntropySlot[ip].d[ static_cast<UINT8*>(addr)[0] ];
		++ReadEntropySlot[ip].d[ static_cast<UINT8*>(addr)[1] ];
		++ReadEntropySlot[ip].d[ static_cast<UINT8*>(addr)[2] ];
		++ReadEntropySlot[ip].d[ static_cast<UINT8*>(addr)[3] ];
	}
}

// Record a memory write record
VOID mem_write( ADDRINT ip, VOID * addr, UINT32 len )
{
	WIP = ip;
	WAddr = addr;
}

VOID mem_write_content( UINT32 len )
{
	if ( len == 1 )
	{
		++WriteEntropySlot[WIP].d[ static_cast<UINT8*>(WAddr)[0] ];
	}
	else if ( len == 2 )
	{
		++WriteEntropySlot[WIP].d[ static_cast<UINT8*>(WAddr)[0] ];
		++WriteEntropySlot[WIP].d[ static_cast<UINT8*>(WAddr)[1] ];
	}
	else if ( len == 4 )
	{
		++WriteEntropySlot[WIP].d[ static_cast<UINT8*>(WAddr)[0] ];
		++WriteEntropySlot[WIP].d[ static_cast<UINT8*>(WAddr)[1] ];
		++WriteEntropySlot[WIP].d[ static_cast<UINT8*>(WAddr)[2] ];
		++WriteEntropySlot[WIP].d[ static_cast<UINT8*>(WAddr)[3] ];
	}
}



// Pin calls this function every time a new instruction is encountered
VOID Inst_Entropy(INS ins, VOID *v)
{
	ADDRINT pc = INS_Address (ins);
	if ( HotMem.find(pc) != HotMem.end() )
	{
		if (INS_IsMemoryWrite(ins))
		{
			INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(mem_write), IARG_INST_PTR, IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_END);

			if (INS_HasFallThrough(ins))
				INS_InsertPredicatedCall(ins, IPOINT_AFTER, AFUNPTR(mem_write_content), IARG_MEMORYWRITE_SIZE, IARG_END);
			if (INS_IsBranchOrCall(ins))
				INS_InsertPredicatedCall(ins, IPOINT_TAKEN_BRANCH, AFUNPTR(mem_write_content), IARG_MEMORYWRITE_SIZE, IARG_END);
		}

		if ( INS_IsMemoryRead(ins) )
			INS_InsertPredicatedCall(ins, IPOINT_BEFORE, AFUNPTR(mem_read), IARG_INST_PTR, IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_END);

		if ( INS_HasMemoryRead2(ins) )
			INS_InsertPredicatedCall(ins, IPOINT_BEFORE, AFUNPTR(mem_read), IARG_INST_PTR, IARG_MEMORYREAD2_EA, IARG_MEMORYREAD_SIZE, IARG_END);


	}
}

double shannon( const Slot & slot )
{
    unsigned int counter = 0;
    for ( size_t i = 0; i < 256; ++i )
        counter += slot.d[i];
    
    double base = 0.0;
	double log2 = log(2.0);
    
	for ( size_t i = 0; i < 256; ++i )
	{
        if ( 0 != slot.d[i] )
		{
            double hertz = 1.0 * slot.d[i] / counter;
            base += log(hertz) / log2 * hertz ;
		}
	}

    return base / -8;
}

// This function is called when the application exits
static VOID Fini_Entropy(INT32 code, VOID *v)
{
	for ( map<ADDRINT, Slot>::const_iterator it = ReadEntropySlot.begin(); it != ReadEntropySlot.end(); ++it )
		fprintf( memTrace, "R|%08x: %f\n", it->first, shannon( it->second ) );
	for ( map<ADDRINT, Slot>::const_iterator it = WriteEntropySlot.begin(); it != WriteEntropySlot.end(); ++it )
		fprintf( memTrace, "W|%08x: %f\n", it->first, shannon( it->second ) );

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

	Slot nullSlot;
	memset( &nullSlot, 0, sizeof(Slot) );

	// init HotMem
	std::ifstream ifs( "config/hotmem.cfg" );
	
	std::string s;
    while( ifs )
    {
		std::getline( ifs, s );
		ADDRINT i;
		sscanf( s.c_str(), "%08x\n", &i );
		HotMem.insert(i);
		ReadEntropySlot[i] = nullSlot;
		WriteEntropySlot[i] = nullSlot;
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
