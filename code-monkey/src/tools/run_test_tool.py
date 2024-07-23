import os
import json
import subprocess
import tempfile
import atexit
from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
)
from constants import artifacts_dir
from instrumentation import instrument
from .utils import make_file_path

def cleanup_temp_file(temp_file):
    if os.path.exists(temp_file):
        os.remove(temp_file)

class RunTestToolInput(BaseModel):
    fname: str = Field(description="Name of the test file to run.")

class RunTestTool(BaseTool):
    """Run Python tests in a given file and return the results"""
    name: str = "run_test"
    description: str = "Run Python tests in a given file and return the results"
    args_schema: Type[BaseModel] = RunTestToolInput


    def summarize_profiling_output(self, prof_file: str) -> dict:
        # The result format looks like this:

        # Thu Jul 25 14:29:12 2024    profile.out
        #
        #          1570092 function calls (1418664 primitive calls) in 0.651 seconds
        #
        #    Ordered by: cumulative time
        #    List reduced from 4208 to 16 due to restriction <'/Users/toshok/src/replayio/ai-playground/code-monkey/src/.*.py'>
        #
        #    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        #         1    0.000    0.000    0.602    0.602 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/test_rg_tool.py:1(<module>)
        #         1    0.000    0.000    0.601    0.601 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/rg_tool.py:1(<module>)
        #         1    0.000    0.000    0.053    0.053 /Users/toshok/src/replayio/ai-playground/code-monkey/src/instrumentation/__init__.py:1(<module>)
        #         1    0.000    0.000    0.037    0.037 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/test_rg_tool.py:11(test_rg_search)
        #         1    0.000    0.000    0.024    0.024 /Users/toshok/src/replayio/ai-playground/code-monkey/src/instrumentation/__init__.py:77(wrapper)
        #         1    0.000    0.000    0.024    0.024 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/rg_tool.py:22(_run)
        #         1    0.000    0.000    0.024    0.024 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/rg_tool.py:28(_search_with_rg)
        #         1    0.000    0.000    0.003    0.003 /Users/toshok/src/replayio/ai-playground/code-monkey/src/constants.py:1(<module>)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/rg_tool.py:13(RgToolInput)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/rg_tool.py:16(RgTool)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/instrumentation/__init__.py:19(tracer)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/test_rg_tool.py:7(setUp)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/instrumentation/__init__.py:76(decorator)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/test_rg_tool.py:6(TestRgTool)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/instrumentation/__init__.py:75(instrument)
        #         1    0.000    0.000    0.000    0.000 /Users/toshok/src/replayio/ai-playground/code-monkey/src/tools/__init__.py:1(<module>)            

        # parse this format and return a dict where keys are `filename:lineno(function)` and values are dicts with keys:
        # ncalls, tottime, percall, cumtime, percall.  each of those keys has a number value.

        rv = dict()

        pstats = subprocess.run(["python", "-c", "import pstats; p = pstats.Stats('profile.out'); p.sort_stats('cumulative').print_stats('/Users/toshok/src/replayio/ai-playground/code-monkey/src/.*.py')"], capture_output=True, text=True)
        pstats_output = pstats.stdout
        lines = pstats_output.split("\n")
        # strip everything to make the comparisons easier
        lines = [line.strip() for line in lines]

        seen_headers = False
        for line in lines:
            # skip everything until we see the line: "ncalls  tottime  percall  cumtime  percall filename:lineno(function)"
            if not seen_headers:
                if line.startswith("ncalls"):
                    seen_headers = True
                continue
            # after the headers, every line has the same format: ncalls  tottime  percall  cumtime  percall filename:lineno(function).  add those to the dict.
            line_parts = line.split(" ")
            line_parts = [part.strip() for part in line_parts]
            line_parts = [part for part in line_parts if part] # remove empty strings
            if len(line_parts)!= 6:
                raise Exception(f"Unexpected line format in profiling output: {line}")

            key = line_parts[5]
            ncalls = int(line_parts[0])
            tottime = float(line_parts[1])
            totpercall = float(line_parts[2])
            cumtime = float(line_parts[3])
            cumpercall = float(line_parts[4])

            rv[key] = { "ncalls": ncalls, "tottime": tottime, "totpercall": totpercall, "cumtime": cumtime, "cumpercall": cumpercall }

            return rv

    @instrument("Tool._run", ["fname"], attributes={ "tool": "RunTestTool" })
    def _run(self, fname: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        # Create a temporary profiling file
        with tempfile.NamedTemporaryFile(delete=False) as prof_file:
            temp_file_path = prof_file.name
            atexit.register(cleanup_temp_file, temp_file_path)

            file_path = make_file_path(fname)

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {fname} does not exist.")

            # Run the test with profiling
            test_command = ["python", "-m", "cProfile", "-o", temp_file_path, "-m", "unittest", file_path]
            print(f"Running test with command: {" ".join(test_command)}")
            result = subprocess.run(
                test_command,
                capture_output=True,
                text=True,
                cwd=artifacts_dir,
            )
            profiling_data = self.summarize_profiling_output(temp_file_path)


            return f"returncode={str(result.returncode)}\nstdout={result.stdout}\nstderr={result.stderr}\nprofiling={json.dumps(profiling_data)}"#