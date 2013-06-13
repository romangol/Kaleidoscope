#include <stdio.h>
#include <map>
#include "pin.H"

using std::map;

static map<ADDRINT, unsigned long> CodeUseDic;
static map<ADDRINT, unsigned long> CodeMemReadDic;
static map<ADDRINT, unsigned long> CodeMemWriteDic;

FILE * InstPool;

static bool RecordFlag = false;

static ADDRINT StartAddr = 0xFFFFFFFF;
static ADDRINT EndAddr = 0xFFFFFFFF;

// Record a memory read record
VOID profile_mem_read( ADDRINT addr )
{
	if ( CodeMemReadDic.find(addr) == CodeMemReadDic.end() )
		CodeMemReadDic[addr] = 0;
	++CodeMemReadDic[addr];
}

// Record a memory write record
VOID profile_mem_write( ADDRINT addr )
{
	if ( CodeMemWriteDic.find(addr) == CodeMemWriteDic.end() )
		CodeMemWriteDic[addr] = 0;
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

	if ( RecordFlag && pc < 0x02000000 )
	{
		// fprintf( InstPool, "%08x|%s\n", pc, INS_Disassemble(ins).c_str() );

		if ( CodeUseDic.find(pc) == CodeUseDic.end() )
			CodeUseDic[pc] = 0;

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
	FILE * fp = fopen( "data/profiler.log", "w");

	for ( map<ADDRINT, unsigned long>::const_iterator it = CodeUseDic.begin(); it != CodeUseDic.end(); ++it )
		fprintf( fp, "C|%08x-%d\n", it->first, it->second );
	for ( map<ADDRINT, unsigned long>::const_iterator it = CodeMemReadDic.begin(); it != CodeMemReadDic.end(); ++it )
		fprintf( fp, "R|%08x-%d\n", it->first, it->second );
	for ( map<ADDRINT, unsigned long>::const_iterator it = CodeMemWriteDic.begin(); it != CodeMemWriteDic.end(); ++it )
		fprintf( fp, "W|%08x-%d\n", it->first, it->second );

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
