FROM ubuntu:20.04

MAINTAINER Li Tai Fang <ltfang@gmail.com>
 
RUN export DEBIAN_FRONTEND=noninteractive && apt update && apt -y install r-base python3 python3-pip bedtools git wget openjdk-8-jdk && apt-get clean
RUN pip3 install cython pysam numpy scipy pandas xgboost
RUN R -e "install.packages('ada', repos = 'http://cran.rstudio.com/')"
RUN cd /opt/ && wget https://www.dropbox.com/s/wbcy4egca3ersl3/GATK-3.4-open-3.1.0-SNAPSHOT.tar && tar -xvf GATK-3.4-open-3.1.0-SNAPSHOT.tar && rm GATK-3.4-open-3.1.0-SNAPSHOT.tar && ln -s GATK-3.4-open-3.1.0-SNAPSHOT GATK
