# differential-fuzzing-of-stateful-systems

# Fuzzing
Run the Docker container in privilegded mode.

Run the following in the container:
```
sudo bash -c 'echo core > /proc/sys/kernel/core_pattern'
```

Fuzz LightFTP inside the docker container:
```
afl-fuzz -t 1000+ -d -i $AFLNET/tutorials/lightftp/in-ftp -o out-lightftp -m none -N tcp://127.0.0.1/2200 -x $AFLNET/tutorials/lightftp/ftp.dict -P FTP -D 10000 -q 3 -s 3 -E -R -c ./ftpclean.sh ./fftp fftp.conf 2200
```

Fuzz Bftpd inside the docker container:
```
afl-fuzz -t 1000+ -d -i $PROFUZZ/in-ftp -o $PROFUZZ/out-ftp/ -m none -N tcp://127.0.0.1/2200 -x $PROFUZZ/ftp.dict -P FTP -D 10000 -q 3 -s 3 -R -c $PROFUZZ/clean.sh /home/ubuntu/bdfpd/./bftpd $PROFUZZ/basic.conf 2200
```

On another instance of the same container, run a TCPdump:
```
sudo tcpdump -i lo -w output.pcap
```

Inside the folder where the flow must be saved extract the TCP streams using TCPflow:
```
tcpflow -r output.pcap
```
Open this folder inside the create_abbadingo.py and run it.

# FlexFringe



Install FlexFringe 

Make a new ini file in the ini folder with
```
[default]
heuristic-name = mealy
data-name = mealy_data
```

Run the following command of the **.dat** file that was previously created:
```
./flexfringe --ini ini/mealy.ini abbadingo.dat
```
Make a graph with **dot**:
```
dot -Tpdf abbadingo.dat.ff.final.dot -o abbadingo-out.pdf
```

#Results
The following results came back for fuzzing LightFTP and Bftpd:

LightFTP:
![alt text](https://github.com/Jer111/differential-fuzzing-of-stateful-systems/blob/main/lightftp_60min.png)
Bftpd:
![alt text](https://github.com/Jer111/differential-fuzzing-of-stateful-systems/blob/main/bftpd_60min.png)
