# Deploy an R application to Google Cloud, using the 'cloudml' package.
import subprocess
import sys
import os

# Construct absolute path to 'deploy.R'.
path, filename = os.path.split(os.path.realpath(__file__))
deploy = os.path.realpath(os.path.join(path, "deploy.R"))
if not os.path.exists(deploy):
  raise IOError("Entrypoint '" + deploy + "' does not exist.")

# Move to the application directory.
os.chdir(os.path.dirname(path))

# Run 'Rscript' with this entrypoint. We don't forward command line arguments,
# as 'gcloud' will append a '--job-dir' argument (when specified) which can
# confuse the tfruns flags system.
commands = [sys.argv[1], deploy]

process = subprocess.Popen(
  commands,
  stdin  = subprocess.PIPE,
  stdout = subprocess.PIPE,
  stderr = subprocess.STDOUT
)

# Stream output from subprocess to console.
for line in iter(process.stdout.readline, ""):
  sys.stdout.write(line)

# Finalize the process.
stdout, stderr = process.communicate()

# Detect a non-zero exit code.
if process.returncode != 0:
  fmt = "Command %s failed: exit code %s"
  print fmt % (commands, process.returncode)
else:
  print "Command %s ran successfully." % (commands, )
