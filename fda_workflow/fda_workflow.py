"""Main module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union, Tuple

from porerefiner.notifiers import Notifier
from porerefiner.jobs import FileJob, RunJob
from porerefiner.jobs.submitters import Submitter
from porerefiner.models import Run, File

import json
import subprocess
import os.path


# @dataclass
# class FdaWorkflowNotifier(Notifier):
#     """Configurable run completion notifier. Implement async method 'notify.'"""

#     fda_workflow_sample_param: str

#     async def notify(self, run: Run, state: Any, message: str) -> None:
#         "Handler for notifications. `state` is not currently implemented."
#         pass

# @dataclass
# class FdaWorkflowSubmitter(Submitter):
#     """Configurable job runner. Implement the below methods."""

#     fda_workflow_sample_param: str

#     async def test_noop(self) -> None:
#         "No-op method submitters should implement to make sure the submitter can access an external resource."
#         pass

#     def reroot_path(self, path: Path) -> Path:
#         "Submitters should translate paths to be relative to execution environment"
#         pass

#     async def begin_job(self, execution_string: str, datadir: Path, remotedir: Path, environment_hints: dict = {}) -> str:
#         "Semantics of scheduling a job. Jobs can provide execution hints. Return an optional job id"
#         pass

#     async def poll_job(self, job:str) -> str:
#         "Semantics of polling a job."
#         pass

# @dataclass
# class FdaWorkflowFileJob(FileJob):
#     """Configurable job that will be triggered whenever a file enters a completed state."""

#     def setup(self, run: Run, file: File, datadir: Path, remotedir: Path) -> Union[str, Tuple[str, dict]]:
#         "Set up the job. Return a string for the job submitter, and optionally a dictionary of execution hints."
#         pass

#     def collect(self, run: Run, file: File, datadir: Path, pid: Union[str, int]) -> None:
#         "Post-job processing. Handle cleanup and make changes to the run or its records."
#         pass

# {
#       "porerefiner_ver": "1.0.0",
#       "library_id": "TEST_TEST",
#       "sequencing_kit": "SQK-LSK109",
#       "barcoding_kit": "SQK-RBK004",
#       "flowcell": "FAK80437",
#       "sequencer": "Revolution",
#       "relative_location": "/FAK80437/FAK80437/20190911_1923_GA10000_FAK80437_bceaf277",
#       "run_month": "11",
#       "run_year": "2019",
#       "run_id": "priceless_wing",
#        "notifications": {
#         "genome_closure_status": [ "Fred.Garvin@fda.hhs.gov", "Veet.Voojagig@fda.hhs.gov" ],
#         "import_ready": [ "Gag.Halfrunt@fda.hhs.gov" ]
#         },
#       "samples": [
#           {
#               "sample_id": "CFSAN00101",
#               "accession": "ACC_TEST_01",
#               "barcode_id": "09",
#               "organism": "Pseudomonas aeruginosa",
#               "extraction_kit": "TEST_KIT_KIT",
#               "comment": " 44",
#               "user": "justin.payne@fda.hhs.gov"
#           }
#      ]
# }



@dataclass
class FdaRunJob(RunJob):
    """  
  - class: FdaRunJob
    config:
      command: module load nanopore-lims/0.1.0 && nanopore_HPC {remote_json} &
      platform: GridION sequence
      closure_status_recipients:
      - justin.payne@fda.hhs.gov
      import_ready_recipients:
      - justin.payne@fda.hhs.gov
    """

    command: str
    platform: str
    closure_status_recipients: list
    import_ready_recipients: list

    def setup(self, run: Run, datadir: Path, remotedir: Path) -> Union[str, Tuple[str, dict]]:
        "Set up the job. Return a string for the job submitter, and optionally a dictionary of execution hints."
        try:
            host = subprocess.run(["hostname"], stdout=subprocess.PIPE).stdout
        except subprocess.CalledProcessError:
            host = "unknown_host"
        # remote_json = os.path.join(self.remote_json_dir, f"{host}_{run.name}.json")
        record = dict(
            porerefiner_ver="1.0.0",
            library_id=run.samplesheet.library_id or "",
            sequencing_kit=run.samplesheet.sequencing_kit or "",
            barcoding_kit=[run.samplesheet.barcoding_kit or ""],
            flowcell=run.flowcell or "",
            sequencer=host,
            relative_location=run.path,
            run_month=run.started.month,
            run_year=run.started.year,
            run_id=run.alt_name,
            notifications=dict(
                genome_closure_status=self.closure_status_recipients or [],
                import_ready=self.import_ready_recipients or [],
            ),
            samples=[
                dict(
                    sample_id=sample.sample_id,
                    accession=sample.accession,
                    barcode_id=sample.barcode_id,
                    organism=sample.organism,
                    extraction_kit=sample.extraction_kit,
                    comment=sample.comment,
                    user=sample.user
                ) for sample in run.samplesheet.samples
            ]
        )

        with open(datadir / f"{host}_{run.name}", 'w') as fp:
            json.dump(record, fp)

        return (self.command.format(**locals()), {}) # execution hints later on, maybe

    def collect(self, run: Run, datadir: Path, pid: Union[str, int]) -> None:
        "Post-job processing. Handle cleanup and make changes to the run or its records."
        pass
