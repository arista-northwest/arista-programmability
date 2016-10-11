PsEapi
======

Simple powershell module for Arista EAPI

Usage
-----

### New-EapiConnection

```powershell
New-EapiConnection [-HostName] <string> [[-Protocol] <string>] [[-UserName] <string>] [[-Password] <string>] [<CommonParameters>]
```

### Invoke-EapiCommands

```powershell
Invoke-EapiCommands [-Commands] <string[]> -Connection <Object> [-Encoding <string>] [<CommonParameters>]
```

### Show-EapiHardwareCapacity

Helper cmdlet for Arad hardware capacity

```powershell
Show-EapiHardwareCapacity [-Connection] <Object>  [<CommonParameters>]
```

Example
-------

### Import the module

```powershell
PS> Import-Module -Force PsEapi.psm1
```

### Run any command...

```powershell
PS > $conn = New-EapiConnection -HostName myswitch -UserName admin -Password ""
PS > $conn | Invoke-EapiCommands "show version"

modelName        : DCS-7508
internalVersion  : 4.16.6M
systemMacAddress : 00:1c:73:3c:ce:b2
serialNumber     : NAN132700420
memTotal         : 15681448
bootupTimestamp  : 1464903383.51
memFree          : 10935184
version          : 4.16.6M
architecture     : i386
isIntlVersion    : False
internalBuildId  : 667e1c30-0ed0-42e6-bd25-53adc03180e5
hardwareRevision : 06.00
```

### Output is an Powershell object, so pipelining works...

Here I'm using a wrapper for the "show hardware capacity" command and filter
the results to only show tables that are greater than 0% full

```powershell
PS> New-EapiConnection -HostName myswitch -UserName admin -Password "" |
>>   Show-EapiHardwareCapacity |
>>   Select-Object -ExpandProperty tables |
>>   Where-Object {$_.usedPercent -gt 0}
highWatermark : 21
used          : 21
usedPercent   : 2
committed     : 0
table         : ECMP
chip          :
maxLimit      : 1023
feature       : Routing
free          : 1002

highWatermark : 646
used          : 633
usedPercent   : 1
committed     : 0
table         : FEC
chip          :
maxLimit      : 31744
feature       : Routing
free          : 31111

highWatermark : 21
used          : 21
usedPercent   : 2
committed     : 0
table         : ECMP
chip          :
maxLimit      : 1023
feature       :
free          : 1002

highWatermark : 646
used          : 633
usedPercent   : 1
committed     : 0
table         : FEC
chip          :
maxLimit      : 31744
feature       :
free          : 31111

highWatermark : 262
used          : 255
usedPercent   : 2
committed     : 1024
table         : TCAM
chip          :
maxLimit      : 12288
feature       : IPv6
free          : 9985
```
