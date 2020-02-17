[![License](https://img.shields.io/badge/License-ASL%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

# Websphere CCT 

**WebSphere Configuration Comparison Tool (WCCT)** is a light weight comparison utility for WebSphere Application Server traditional.  Use of this tool is a two step process.  The first step is gathering data from the configuration repository using the wsadmin script ConfigDump.py.  The second is generating HTML reports to display configuration differences.  Manually configured application servers and resources are likely to have configuration differences. Finding these differences by navigating to configuration panels is error prone and time consuming. Applications servers and resources should be periodically checked for configuration differences.  Note, please reference [WASConfigurationComparisonTool.pdf](WASConfigurationComparisonTool.pdf) for full documentation.  

WCCT provides a facility to check multiple server and resource configurations for:
- potential inconsistent behavior between application servers in a cluster.
- configuration creep.
- migration of configuration from version to version.
- file system differences.

## Current WCCT reports include:
- Application Servers
- Node Agents
- Global Security configuration (not Domain Security)
  - Trust Association (Global and Domain)
- SSL Configurations
- Data Sources
- J2C Resource Adapters
- JDBC Drivers
- Object Cache instances
- Servlet Cache instances
- Service Integration Bus instances
- Resource Environment Providers
- Resource Environment Entries
- JMS Queues, Topics Providers and Activation Specifications, JAAS Auth Data
- File system comparisons

## CCT usage scenarios:
- Isolating configuration creep: Periodic configuration snapshots can be gathered and archived. These can be used to see what configuration changes that have been made over time.
- Troubleshooting inconsistent cluster member configuration: Servers and node/server specific resource configuration anomalies can causes unexpected runtime behavior from different servers within a cluster.
- Assisting in migration to a new version of WebSphere: Cross version configuration reports can help ensure a complete migration of server and resource settings.

## Tar File Contents:
- [ConfigReport.py](ConfigReport.py): Script for creating reports for Traditional Profile WebSphere
- [ConfigDump.py](ConfigDump.py): wsadmin script for dumping configuration
- [ConfigUtils.py](ConfigUtils.py): Utilities script
- [WAuJ.py](WAuJ.py): Utilities script
- [WAuJ_utilities.py](WAuJ_utilities.py): Utilities script
- [ConfigReport.properties](ConfigReport.properties): Sample properties file for defining reports for Traditional Profile WebSphere
- [ConfigReportAttributes.properties](ConfigReportAttributes.properties): Defines attributes reported in Traditional Profile WebSphere reports.  It is recommended not to edit this.
- [CollectFileData.sh](CollectFileData.sh): Collects file data from the specified file system
- [ConfigReportFiles.py](ConfigReportFiles.py): Generates file system comparison reports
- [WASConfigurationComparisonTool.pdf](WASConfigurationComparisonTool.pdf): Tool documentation

## Contributing

This project uses the [Developer's Certificate of Origin 1.1 (DCO)](https://github.com/hyperledger/fabric/blob/master/docs/source/DCO1.1.txt) see [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Change History:

See [CHANGELOG.md](CHANGELOG.md) for more details.