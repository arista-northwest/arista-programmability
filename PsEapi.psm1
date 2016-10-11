
function New-EapiConnection {
  [CmdletBinding()]
  Param (
    [Parameter(Mandatory=$True)]
    [string] $HostName,
    [Parameter()]
    [string] $Protocol = "http",
    [Parameter()]
    [string] $UserName = "admin",
    [Parameter()]
    [string] $Password = ""
  )

  $Uri = "{0}://{1}/command-api" -f $Protocol, $HostName
  $Connection = (New-Object PSObject |
    Add-Member -PassThru NoteProperty Uri $Uri |
    Add-Member -PassThru NoteProperty UserName $UserName |
    Add-Member -PassThru NoteProperty Password $Password)

  $Connection
}

function Invoke-EapiCommands {
  [CmdletBinding()]
  Param (
    [Parameter(Mandatory=$True, ValueFromPipeline=$True)]
    [object] $Connection,
    [Parameter(Mandatory=$True, Position=1)]
    [string[]] $Commands,
    [Parameter()]
    [string] $Encoding = "json"
  )

  # Create Object and convert to JSON
  $Params = @{version = 1; cmds = $Commands; format = $Encoding}

  # Create the JSON object
  $Payload = (New-Object PSObject |
    Add-Member -PassThru NoteProperty jsonrpc '2.0' |
    Add-Member -PassThru NoteProperty method 'runCmds' |
    Add-Member -PassThru NoteProperty params $Params |
    Add-Member -PassThru NoteProperty id '1') | ConvertTo-Json

  # Create ASCII encoded version of the JSON string
  $Payload = [System.Text.Encoding]::ASCII.GetBytes($Payload)

  [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$True}

  $Request = [System.Net.WebRequest]::Create($Connection.Uri)
  $Request.Method = "POST"
  $Request.ContentType = "application/json"
  $Request.Credentials = New-Object System.Net.NetworkCredential `
    -ArgumentList $Connection.UserName, $Connection.Password

  $Stream = $Request.GetRequestStream()
  $Stream.Write($Payload, 0, $Payload.Length)
  $Stream.close()

  $Reader = New-Object System.IO.StreamReader `
    -ArgumentList $Request.GetResponse().GetResponseStream()

  $Response = $Reader.ReadToEnd() | ConvertFrom-Json
  $Reader.Close()

  $Response.Result
}

function Show-EapiHardwareCapacity
{
  [CmdletBinding()]
  Param (
    [Parameter(Mandatory=$True, ValueFromPipeline=$True)]
    [object] $Connection
  )

  $Connection | Invoke-EapiCommands -Commands "show hardware capacity"
}

Export-ModuleMember New-EapiConnection, Invoke-EapiCommands,
  Show-EapiHardwareCapacity
