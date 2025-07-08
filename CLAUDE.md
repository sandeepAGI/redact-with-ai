I tested it in streamlit and it have a couple of observations:
1) After the document has been anonymized - there is no link to either download it or a way to preview or see it
2) I got this error on the results page "KeyError: 'overall_score'
Traceback:
File "/opt/anaconda3/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 542, in _run_script
    exec(code, module.__dict__)
File "/Users/sandeepmangaraj/myworkspace/Utilities/smart-redact/main.py", line 420, in <module>
    f"{overall_result['overall_score']:.1f}/100",
       ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^"
3) Some instructions - maybe in the left Navigation panel will be helpful