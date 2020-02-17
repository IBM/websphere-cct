# websphere-cct
WebSphere Configuration Comparison Tool (WCCT) is a light weight comparison utility for WebSphere Application Server Traditional profile.  Use of this tool is a two step process.  The first step is gathering data from the configuration repository using the wsadmin script ConfigDump.py.  The second is generating HTML reports to display configuration differences.  Manually configured application servers and resources are likely to have configuration differences. Finding these differences by navigating to configuration panels is error prone and time consuming. Applications servers and resources should be periodically checked for configuration differences.  Note, please reference WASConfigurationComparisonTool.pdf for full documentation.  

WCCT provides a facility to check multiple server and resource configurations for:
- potential inconsistent behavior between application servers in a cluster.
- configuration creep.
- migration of configuration from version to version.
- file system differences.


Current WCCT reports include:
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

CCT usage scenarios:
- Isolating configuration creep: Periodic configuration snapshots can be gathered and archived. These can be used to see what configuration changes that have been made over time.
- Troubleshooting inconsistent cluster member configuration: Servers and node/server specific resource configuration anomalies can causes unexpected runtime behavior from different servers within a cluster.
- Assisting in migration to a new version of WebSphere: Cross version configuration reports can help ensure a complete migration of server and resource settings.

Tar File Contents:
- ConfigReport.py: Script for creating reports for Traditional Profile WebSphere
- ConfigDump.py: wsadmin script for dumping configuration
- ConfigUtils.py: Utilities script
- WAuJ.py: Utilities script
- WAuJ_utilities.py: Utilities script
- ConfigReport.properties: Sample properties file for defining reports for Traditional Profile WebSphere
- ConfigReportAttributes.properties: Defines attributes reported in Traditional Profile WebSphere reports.  It is recommended not to edit this.
- CollectFileData.sh: Collects file data from the specified file system
- ConfigReportFiles.py: Generates file system comparison reports
- WASConfigurationComparisonTool.pdf: Tool documentation

Change history:
- January 30th, 2020
  - Added various JMS reports.
  - Made ReportList and ConfigurationDumpFiles optional properties for simplified command line syntax.
  - Added capability to filter out top level object types from collection. 
- August 22nd 2019
  - More documentation updates. 
- August 21st 2019
  - Documentation updates. 
- August 19th 2019
  - Corrected report generation failure in SSL cipher reporting.
  - Added support for collecting file system data for AIX.
  - Added optional parameter on ConfigDump.py to set the cell suffix from the command line.
  - Improved syntax help on ConfigReportFiles.py
  - Added the ability to only collect data from specified scopes.
- June 6th 2019
  - Changed files that match in CRC and size but not date and time to be a conditional correct match.
  - Corrected issue with Trust Association report generation.
  - Disabled specific error messages in ConfigDump.py.
  - Added more documentation for file system reports.
  - Reordered documentation for better flow.
- April 3rd, 2019
  - Reports on Trust Association and Trust Association Interceptor configuration.
  - Light weight file system comparison using date, time and chksum of files.
- December 29th, 2018
  - Generate sample wsadmin scripts which will make configuration values consistent for resources identified in a given report. 
- November 14, 2018
  - Added application comparison reports.
    - Built in "Applications" report that compares configurations by deployed module name.
    - User defined reports that allow comparing any applications with each other.
  - Updated documentation.
    - Reordered presentation pages.
    - Added page for installation instructions
    - Added page detailing available resource reports
    - Added page detailing built in reports. 
- October 31, 2018
  - Corrected character truncation for generic JVM arguments as well as extraneous characters with leading and trailing arguments. 
- August 3, 2018
  - Resource Environment Provider reports.
  - Resource Environment Entry reports.
- August 2, 2018
  - Corrected issue in ConfigDump.py preventing it from running. 
  - Accounted for configuration anomalies with incomplete and orphaned variable substitution entries.
  - Corrected path separator issue on Linux for report generation.
- June 17th, 2018
  - Added ability to compare all SSL configurations, not just cell defaults.
  - Enhanced Resources report to compare SSL configurations by the same name automatically.
  - Added cipher report to compare which ciphers may be inconsistent between SSL configs.
  - Updated ConfigDump.py to explicitly gather configuration data for all SSL configurations. Configuration dumps done with prior versions of ConfigDump.py may not pick up all SSL configurations.
  - Enhanced Cell Summary report to list all SSL Configuration aliases and scopes.
  - Corrected a bug which broke individual JVM argument comparisons.
- June 2nd, 2018
  - New report properties file processing introduced.
  - Individual report properties may be set on the command line.
  - Reports may be abbreviated to attributes that have differences only.
  - A node agent report was added.
  - Thread Pool Manager and all thread pools are now reported.
- May 27th, 2018
  - Added a report key at the top of all report documenting values in match column and cell background colors.
  - Added capability to replace a string with another value or a regular expression for the purposes of matching.
  - Cell, node and server names are replaced with .* by default for matching purposes.
- January 19th, 2018
  - ConfigDump.py on Windows systems that do not have a Unix shell (sh) will fail. Added messages documenting a workaround.
  - Updated PDF presentation with ConfigReport.py prerequisites and syntax.
- January 17th, 2018
  - Initial publication
