#!/bin/bash
cd
module load python/3.8
virtualenv ~/cdcbirth
source ~/cdcbirth/bin/activate
pip install --no-index --upgrade pip
pip install --no-index pandas scipy scikit_learn matplotlib seaborn plotly
pip install --no-index jupyterlab
# pip install python-dotenv # don't think I need this????

# create bash script for opening jupyter notebooks https://stackoverflow.com/a/4879146/9214620
cat << EOF >$VIRTUAL_ENV/bin/notebook.sh
#!/bin/bash
unset XDG_RUNTIME_DIR
jupyter-lab --ip \$(hostname -f) --no-browser
EOF

chmod u+x $VIRTUAL_ENV/bin/notebook.sh