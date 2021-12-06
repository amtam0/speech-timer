## EFREI setup

#### Installations
1. Docker / docker-compose : https://docs.docker.com/get-docker/
To get used to basic commands check : https://docs.docker.com/get-started/

2. Ngrok : is a local tunnel URL that is essential to share Webapps during annotation process.
You need to create 2 accounts from this link https://ngrok.com/ and copy the 2 authtokens
Download Ngrok depending on your OS, and add it to the home folder (unzipped Drive)

3. download and unzip the folder in Drive
add Authtokens (from ngrok) in ngrok_ML.yml and nrok_LS.yml respectively.
#### Start/Expose labelstudio
- To start Labelstudio
```
./ngrok start --config=ngrok_LS.yml labelstudio #use the shown url in the next command
```
- Specify the ngrok url shown to run Labelstudio
```
cd labelstudioUI
LABEL_STUDIO_HOST=https://....ngrok.io docker-compose up
```
The Labelstudio Webapp will be accessible via the Url https://....ngrok.io

#### Config labelstudio
1. Create new project and give it a name (Ex. NER1)

2. In Labeling Interface, use this template (copy/paste)
Go to Project > Settings > Labelling Interface and copy/paste the xml below. It specifies the entities that will be used for annotation
```
<View>
  <Labels name="label" toName="text">
    <Label value="nb_rounds"/>
    <Label value="duration_br_sd"/>
    <Label value="duration_br_min"/>
    <Label value="duration_br_hr"/>
    <Label value="duration_wt_sd"/>
    <Label value="duration_wt_min"/>
    <Label value="duration_wt_hr"/>
  </Labels>
  <Text name="text" value="$text" valueType="url"/>
</View>
```

<img src="doc-imgs/config.png" width=500px/>

3. In settings > General select random sampling

<img src="doc-imgs/random_sample.png" width=500px/>

#### load data in labelstudio
`cd notebooks; jupyter notebook`
change these variables in **NER_create_dataset.ipynb**
- TOKEN: Go to Account and Settings and copy Access Token
- HOST : ngrok url (not localhost) that gives access to Labelstudio

- Run the notebook
it will create the dataset in **training/data/unlabeled/task.json**
and send it to Labelstudio

Start annotation !

Note : use the Label all task button to start annotation (recommended)
<img src="doc-imgs/labelling.png" width=500px/>

#### Setup / Connect ML backend
- Setup env, do it once
```
conda create -n labelstudioml python=3.8
conda activate labelstudioml
conda install nb_conda
pip install jupyter flair==0.9.0
git clone https://github.com/heartexlabs/label-studio-ml-backend
cd label-studio-ml-backend
pip install -U -e .
```
- To init / reset Labelstudio ML backend
```
cd ..
label-studio-ml init my-ml --script models/flairner.py --force
```
- To start the ML BACKEND
1. Start your backend
```
label-studio-ml start ./my-ml/ --port=4000 --host=localhost --debug
```
2. run Ngrok to tunnel http://localhost:4000
```
./ngrok start --config=ngrok_LS.yml labelstudio #use the shown url in the next command
```
CLick the link that will show up to access the Api


- To connect ML backend to Labelstudio check screen below

<img src="doc-imgs/mlbackend.png" width=500px/>
