Arista Programmability Intro
============================

Preparation
-----------

### Requirements

- Windows 10 Enterprise or professional
- 8GB Ram
- 4 Cores

### Clone the repo

PS > cd <path-to-projects>
PS > git clone https://github.com/arista-northwest/arista-programmability.git


### EosSdk Stubs

1. Download from: https://www.arista.com/en/support/software-download
   * Expand "EOS SDK" -> "v1.8.0"
   * Click on: EosSdk-stubs-1.8.0.tar.gz

2. Copy the tar.gz file to the arists-programmability project folder

3. Docker build will take care of the rest

### Docker

1. Enable Hyper-V
  * Type "Turn Windows features on or off" in the taskbar
  * Check Hyper-V (if not available check virtualization feature in your BIOS)

2. Download and install Docker from: https://www.docker.com/products/docker#/windows

3. Build and run the container

```ps1
cd <path-to-projects>/arista-programmability
docker build -t ubuntu:arista-prog .
docker run -it -v <path-to-projects>/arista-programmability:/opt/arista-prog `
  ubuntu:arista-prog
```

### vEOS

1. Running-config for lab VM

```
! Command: show running-config
! device: veos (vEOS, EOS-4.17.1.1F-3512479.41711F (engineering build))
!
! boot system flash:/vEOS-lab.swi
!
alias ship show ip interface
!
transceiver qsfp default-mode 4x10G
!
hostname veos
!
spanning-tree mode mstp
!
aaa authorization exec default local
!
aaa root secret root
aaa authentication policy local allow-nopassword-remote-login
!
username admin privilege 15 role network-admin nopassword
!
interface Management1
   description Connected to DockerNAT vswitch
   ip address 10.0.75.100/24
!
no ip routing
!
management api http-commands
   protocol http
   no shutdown
!
!
end
```

### Building switch agents

```ps1
#!/bin/sh
g++ -std=gnu++0x -o /opt/arista-p/MyAgent.o /opt/arista-p/MyAgent.cpp -leos
```
