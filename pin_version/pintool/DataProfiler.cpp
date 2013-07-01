#include <stdio.h>
#include "pin.H"

FILE * InstPool;

static bool RecordFlag = false;

static ADDRINT StartAddr = 0xFFFFFFFF;
static ADDRINT EndAddr = 0xFFFFFFFF;

static unsigned int CodeUseDic[0x1000000] = {0};
static unsigned int CodeMemReadDic[0x1000000] = {0};
static unsigned int CodeMemWriteDic[0x1000000] = {0};

static unsigned int MinAddr = 0xFFFFFFFF;
static unsigned int MaxAddr = 0;

// Record a memory read record
VOID profile_mem_read( ADDRINT addr )
{
	++CodeMemReadDic[addr];
}

// Record a memory write record
VOID profile_mem_write( ADDRINT addr )
{
	++CodeMemWriteDic[addr];
}

VOID profile_code( ADDRINT addr )
{
	++CodeUseDic[addr];
}



// Pin calls this function every time a new instruction is encountered
VOID Inst(INS ins, VOID *v)
{
	ADDRINT pc = INS_Address (ins);
    if ( pc == StartAddr )
    	RecordFlag = true;
    if ( pc == EndAddr )
    	RecordFlag = false;

	if ( RecordFlag && pc < 0x01000000 )
	{
		if ( MinAddr > pc )
			MinAddr = pc;
		if ( MaxAddr < pc )
			MaxAddr = pc;

		INS_InsertCall( ins, IPOINT_BEFORE, (AFUNPTR)profile_code, IARG_INST_PTR, IARG_END );

		if (INS_IsMemoryWrite(ins))
			INS_InsertCall(ins, IPOINT_BEFORE, AFUNPTR(profile_mem_write), IARG_INST_PTR, IARG_END);
		
		if ( INS_HasMemoryRead2(ins) )
			INS_InsertPredicatedCall(ins, IPOINT_BEFORE, AFUNPTR(profile_mem_read), IARG_INST_PTR, IARG_END);


		if ( INS_IsMemoryRead(ins) )
			INS_InsertPredicatedCall(ins, IPOINT_BEFORE, AFUNPTR(profile_mem_read), IARG_INST_PTR, IARG_END);
	}
}


// This function is called when the application exits
VOID Finish(INT32 code, VOID *v)
{
	printf( "MinAddr:%08x, MaxAddr:%08x\n", MinAddr, MaxAddr );

	FILE * fp = fopen( "data/profiler.log", "w");

	for ( size_t i = MinAddr; i <= MaxAddr; ++i )
	{
		if ( CodeUseDic[i] != 0 )
			fprintf( fp, "C|%08x-%d\n", i, CodeUseDic[i] );
		if ( CodeMemReadDic[i] != 0 )
			fprintf( fp, "R|%08x-%d\n", i, CodeMemReadDic[i] );
		if ( CodeMemWriteDic[i] != 0 )
			fprintf( fp, "W|%08x-%d\n", i, CodeMemWriteDic[i] );
	}

	fclose(fp);
	fclose( InstPool );
	puts("--FINI--\n");
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage_Profiler()
{
    PIN_ERROR("This Pintool prints the IPs of every instruction executed\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}

int profiler(int argc, char * argv[])
{
    // Initialize pin
    if ( PIN_Init(argc, argv) )
		return Usage_Profiler();

	InstPool = fopen("data/instPool.out", "w");
	printf( "Start Address:" );
	scanf( "%08x", &StartAddr );
	printf( "End Address:" );
	scanf( "%08x", &EndAddr );

	printf( "Start:%08x\tEnd:%08x\n", StartAddr, EndAddr );


    // Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(Inst, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Finish, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
