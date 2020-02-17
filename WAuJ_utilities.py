##########################################################################################
# 
# Copyright International Business Machines Corp. 2014, 2020.
# 
# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership. Licensed under the Apache License,
# Version 2.0 (the "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
#-------------------------------------------------------------------------------
#    Name: WAuJ_utilities
#    From: WebSphere Application Server Administration using Jython
#      By: Robert A. (Bob) Gibson [rag], Arthur Kevin McGrath, Noel J. Bergman
#    ISBN: 0-137-00952-6
#    Role: Module used to contain some useful routines
#    Note: Depends upon availability of WSAS scripting objects via sys.modules
#          See WAuJ.py
#   Usage: import WAuJ_utilities as WAuJ
#
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 13/05/04  rag 0.49 Fix - unravel()                                               -> 0.5
# 13/05/03  rag 0.48 Fix - configIdAsDict                                          -> 0.6
# 12/06/28  rag 0.47 Fix - memberInfo() and configIdAsDict() prologues updated     -> 0.0
#                          to add information about ambiguous names
# 12/05/18  rag 0.46 Add - parentTypes()                                           -> 0.0
# 11/11/30  rag 0.45 Add - displayWSASvars()                                       -> 0.0
# 11/10/12  rag 0.44 Fix - displayOperations()                                     -> 0.3
# 11/10/12  rag 0.43 Fix - displayOperations()                                     -> 0.2
# 11/10/12  rag 0.42 Fix - displayOperations()                                     -> 0.1
# 11/09/22  rag 0.41 Fix - WSASvariables()                                         -> 0.5
# 11/09/14  rag 0.40 Fix - displayDict()    - properly parse configId list         -> 0.8
#                          configIdAsDict() - allow configId names to have hyphen  -> 0.5
# 11/09/07  rag 0.39 Fix - configIdAsDict() - allow configId names to have periods -> 0.4
# 11/06/20  rag 0.38 Add - displayNodeVersions                                     -> 0.0
# 11/06/03  rag 0.37 Fix - unravel()                                               -> 0.4
#                    Fix - fullSync()                                              -> 0.1
# 11/05/20  rag 0.36 Fix - certAsDict()  : check for type( '' ) or type( u'' )     -> 0.2
#                    Fix - displayDict() : check for type( '' ) or type( u'' )     -> 0.7
#                    Fix - displayAttributes() prologue comment                    -> 0.1
# 11/05/13  rag 0.35 Fix - findScopedTypes()                                       -> 0.1
# 11/05/10  rag 0.34 Fix - WSASvariables()                                         -> 0.4
# 11/05/02  rag 0.33 Add - unravel() special check for ${SERVER} on NODE_AGENT     -> 0.3
#                    Fix - WSASvariables() - make v 6.1 compatible                 -> 0.3
# 11/04/30  rag 0.32 Del - Removed extraneous ';' line separator semicolons
#                    Fix - unravel() to use string.replace(), not RE.sub()         -> 0.2
# 11/04/27  rag 0.31 Fix - MBattrAsDict()                                          -> 0.2
#                          showAsDict()                                            -> 0.2
#                    Add - fullSync()                                              -> 0.0
# 11/04/03  rag 0.30 Add - displayAttributes()                                     -> 0.0
# 11/02/04  rag 0.29 Add - displayOperations()                                     -> 0.0
# 10/10/01  rag 0.28 Add - certAsDict() [moved from Certzilla.15.py]               -> 0.1
# 10/09/29  rag 0.27 Fix - configurable()                                          -> 0.1
#                    Add - code to implied/anonymous main to import scripting objects
#                          which is really only needed for WAS 6.1 environments.
# 10/09/27  rag 0.26 Fix - scopeAsDict()                                           -> 0.1
#                    Add - displayDict() : Handle nested dictionaries & non-stings -> 0.6
# 10/09/24  rag 0.25 Add - scopeAsDict()                                           -> 0.0
#                          scopeNameAsDict()                                       -> 0.0
# 10/06/24  rag 0.24 Add - findScopedTypes()                                       -> 0.0
#                    Fix - Rename findNamedConfigType as firstNamedConfigType      -> 0.1
# 10/06/04  rag 0.23 Add - findTypes()
# 10/05/28  rag 0.22 Fix - displayDict()                                           -> 0.5
# 10/05/24  rag 0.21 Add - configurable()                                          -> 0.0
# 10/05/19  rag 0.20 Fix - scopedWSASvariables()                                   -> 0.2
#                    Fix - configIdFilter()                                        -> 0.1
#                    Fix - WSASvariables()                                         -> 0.2
# 10/05/13  rag 0.19 Fix - displayDict() display double quoted "list" values correctly
# 10/05/12  rag 0.18 Add - displayDict() function to better display "list" values
# 10/04/22  rag 0.17 Add - Change docstrings to include routine signatures,
#                          add findNamedConfigType(), getEndPointName(),
#                          getEndPoints(), getPort(), getPorts()
#                    Fix - WSASvariables()                                         -> 0.1
# 10/04/19  rag 0.16 Fix - unravel() - check for '[]' (empty string)
# 10/04/18  rag 0.15 Add - scopedWSASvariables(), WSASvariables() & unravel()
# 10/04/17  rag 0.14 Add - Example use for configIdFilter()
# 10/04/16  rag 0.13 Add - Add configInfoAsDict(), cellInfo(), nodeInfo(),
#                          memberInfo(), serverInfo(), configIdFilter().
#                          Rewrite clusterInfo() using configInfoAsDict().
# 10/04/15  rag 0.12 Fix - Add callerName docstring
# 10/04/08  rag 0.11 Fix - displayDict() to not die if the dictionary is empty
# 10/01/27  rag 0.10 Add - callerName()
# 09/12/07  rag 0.9  Fix - brackGroups() - correctly handle nested brackets
# 09/11/15  rag 0.8  Fix - stringListAsList()
#                    Add - docstring for brackGroups(), nvListAsDict(),
#                          nvTextListAsDict(), stringAsNestedList()
#                          stringListAsList()
#                    Add - localMode()
# 09/11/14  rag 0.7  Fix - Rewrite clusterInfo()
#                    Add - version number and lastUpdated variables
#                    Add - displayDict() optional parameter: width
#                    Add - stringListAsList()
# 09/08/18  rag 0.6  Add - bracketGroups(), nvListAsDict() &
#                          stringAsNestedList()
# 09/04/07  rag 0.5  Add - displayDict() routine
# 09/03/21  rag 0.4  Fix - corrected nvTextListAsDict() comments
# 08/12/17  rag 0.3  Add - nvTextListAsDict() routine
# 08/12/09  rag 0.2  Add - docstring for fixFileName() & Usage() routines
# 08/11/07  rag 0.1  Add - docstring
# 08/10/31  rag 0.0  New - for the book
#-------------------------------------------------------------------------------
'''
     From: WebSphere Application Server Administration using Jython (WAuJ)
       By: Robert A. (Bob) Gibson, Arthur Kevin McGrath, Noel J. Bergman
Published: IBM Press - Oct 2009
     ISBN: 0-137-00952-6
     Role: Provide a collection of library routines to assist with the
           Administration of a WebSphere Application Server environment.
'''

version     = '0.49'
lastUpdated = '04 May 2013'  # StarWars day : May the 4th be with you

import sys, re               # Make these libraries available for all

#-------------------------------------------------------------------------------
# Name: bracketGroups()
# Role: Routine used to process a string containing matching bracket
#       (i.e., []), and return a list containing the string positions
#       of these bracket pairs.
# Note: A malformed input string can cause an exception.
# Example:
#   >import WAuJ_utilities as WAuJ
#   >WAuJ.bracketGroups( '[name value][name value]' )
#   [[0, 11], [12, 23]]
#   >WAuJ.bracketGroups( '[[name value][name value]]' )
#   [[0, 25], [1, 12], [13, 24]]
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 09/12/07  rag 0.2  Fix - rewrite to properly return nested list values
# 09/11/15  rag 0.1  Add - docstring
# 09/08/18  rag 0.0  New - Use to validate input strings containing
#                          bracketed groups.
#-------------------------------------------------------------------------------
def bracketGroups( string ) :
  'bracketGroup( string ) - Process a string containing matching brackets, returning a list of string positions of the matching brackets'
  result = []                          # Build the result list as we go
  pair   = []                          # Current pair of values - stack
  for offset in range( len( string ) ) :
    c = string[ offset ]               # Current character in string
    if c == '[' :                      # Open bracket?
      here = [ offset ]                # Yes - add a new list to result
      result.append( here )            #
      pair.append( result[ -1 ] )      #       and add a binding to pair
                                       #
    if c == ']' :                      # Closing bracket?
      here = pair.pop()                # Remove top of stack from pair
      here.append( offset )            # Append closing offset to it
                                       #
  return result                        # Return the list of bracket pair offsets


#-------------------------------------------------------------------------------
# Name: callerName
# Role: Utility routine used to determine, and return the name of the
#       function that called it.
# Note: Dependent upon sys._getframe()
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/15  rag 0.1  Add - docstring
# 10/01/27  rag 0.0  New - See http://code.activestate.com/recipes/66062/
#-------------------------------------------------------------------------------
def callerName() :
  "callerName() - Returns the name of the calling routine (or '?')"
  return sys._getframe( 1 ).f_code.co_name


#-------------------------------------------------------------------------------
# Name: cellInfo()
# Role: Return a dictionary having the primary key being the unique
#       cell name(s), and the values being the associated configID
#       for that cell
# Example: clusters = clusterInfo()
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/16  rag 0.0  New - Write using configInfoAsDict()
#-------------------------------------------------------------------------------
def cellInfo() :
  'cellInfo() - Return a dictionary of the cell names, and their configuration IDs.'
  return configInfoAsDict( 'Cell' )


#-------------------------------------------------------------------------------
# Name: certAsDict()
# Role: Parse the specified certificate string, and return a dictionary
#       containing the certificate specific details.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/05/20  rag 0.2  Add - test for a string, or unicode string
# 10/04/16  rag 0.1  Add - Move from Certzilla.15.py & add error checking
# 10/04/16  rag 0.0  New - Write using configInfoAsDict()
#-------------------------------------------------------------------------------
def certAsDict( cert ) :
  'Parse given certificate (string) returning a dictionary of its contents.'
  funName = callerName()               # Dynamically determine function name
  result = {}                          # Returned dictionary
  if type( cert ) == type( '' ) or type( cert ) == type( u'' ) :
    if cert :                          # Is cert empty?
      if ( cert[ 0 ] == '[' ) and ( cert[ -1 ] == ']' ) and ( cert.count( '[' ) == cert.count( ']' ) ) :
        cert = cert[ 1:-1 ].strip()
        for start, stop in bracketGroups( cert ) :
          field = cert[ start : stop + 1 ]
          if ( field[ 0 ] == '[' ) and ( field[ -1 ] == ']' ) and ( field.count( '[' ) == field.count( ']' ) ) :
            name, value = field[ 1:-1 ].split( ' ', 1 )
            #-------------------------------------------------------------------
            # Only keep field elements having alphabetic field names...
            #-------------------------------------------------------------------
            if name.isalpha() :
              result[ name ] = value
      else :
        print '%s() Error: Unexpected certificate format: "%s"' % ( funName, cert ) 
    else :
      print '%s() Error: Unexpected parameter value: "%s"' % ( funName, cert )
  else :
    print '%s() Error: Unexpected parameter type: %s' % ( funName, type( cert ) )
  return result


#-------------------------------------------------------------------------------
# Name: configIdAsDict
# Role: Utility routine used to return a dictionary of name/value
#       details from an configuration ID (configID)
# Note: Exception handler requires sys module
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 13/05/03  rag 0.6  Fix - Allow name to have dash / hyphen (i.e., '-')
#                    Fix - Warning message for better alignment
#                    Note: Somehow the 0.5 fix appears to have gotten lost
# 11/09/14  rag 0.5  Fix - Allow name to have dash / hyphen '-'
# 11/09/07  rag 0.4  Fix - Allow name to have periods
# 09/08/11  rag 0.3  Fix - Check for & handle double quoted configIDs
# 08/12/03  rag 0.2  Mod - Change "unexpected situation" message
# 08/11/04  rag 0.1  Add - Add the "Name" attribute to the dictionary
# 08/10/27  rag 0.0  New - insight obtained while writing the book
#-------------------------------------------------------------------------------
def configIdAsDict( configId ) :
  'configIdAsDict( configId ) - Given a configID, return a dictionary of the name/value components.'
  funName = callerName()               # Name of this function
  result  = {}                         # Result is a dictionary
  hier    = []                         # Initialize to simplifiy checks
  try :                                # Be prepared for an error
    #---------------------------------------------------------------------------
    # Does the specified configID match our RegExp pattern?
    # Note: mo == Match Object, if mo != None, a match was found
    #---------------------------------------------------------------------------
    if ( configId[ 0 ] == '"' ) and ( configId[ -1 ] == '"' ) and ( configId.count( '"' ) == 2 ) :
      configId = configId[ 1:-1 ]
    mo = re.compile( r'^([\w .-]+)\(([^|]+)\|[^)]+\)$' ).match( configId )
    if mo :
      Name = mo.group( 1 )
      hier = mo.group( 2 ).split( '/' )
    if mo and ( len( hier ) % 2 == 0 ) :
      #-------------------------------------------------------------------------
      # hier == Extracted config hierarchy string
      #-------------------------------------------------------------------------
      for i in range( 0, len( hier ), 2 ) :
        ( name, value ) = hier[ i ], hier[ i + 1 ]
        result[ name ]  = value
      if result.has_key( 'Name' ) :
        print '''%s: Unexpected situation - "Name" attribute conflict,
  Name = "%s", Name prefix ignored: "%s"''' % ( funName, result[ 'Name' ], Name )
      else :
        result[ 'Name' ] = Name
    else :
      print '''%(funName)s:
  Warning: The specified configId doesn\'t match the expected pattern,
           and is ignored.
 configId: "%(configId)s"''' % locals()
  except :
    ( kind, value ) = sys.exc_info()[ :2 ]
    print '''%(funName)s: Unexpected exception.\n
  Exception  type: %(kind)s
  Exception value: %(value)s''' % locals()
  return result


#-------------------------------------------------------------------------------
# Name: configIdFilter()
# Role: Return either a single configID, or None.
# Note: If more than 1 configID generated, None is returned.
#       Useful for locating a specific configuration ID based upon a
#       specific sequence (pattern) of characters that the configID
#       must contain.
#
# For Example:
#       Given the configID for a specific AppServer, we know that the
#       configID of the associated Node will have the same cell and
#       node as the server.
#
#   wsadmin>import WAuJ_utilities as WAuJ
#   wsadmin>
#   wsadmin>server = AdminConfig.list( 'Server' ).splitlines()[ -1 ]
#   wsadmin>server
#   'server1(cells/ragweedCell02/nodes/ragweedNode03/servers/...)'
#   wsadmin>
#   wsadmin>cfgDict = WAuJ.configIdAsDict( server )
#   wsadmin>nodeIdPrefix = '(cells/%(cells)s/nodes/%(nodes)s|' % cfgDict
#   wsadmin>nodeIdPrefix
#   '(cells/ragweedCell02/nodes/ragweedNode03|'
#   wsadmin>node = WAuJ.configIdFilter( 'Node', nodeIdPrefix )
#   wsadmin>node
#   'ragweedNode03(cells/ragweedCell02/nodes/ragweedNode03|node.xml#Node_1)'
#
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/05/19  rag 0.1  Add - additional debug information
#                    Fix - return an empty string instead of None.
#                    Fix - handle len( result ) == 0 quietly
# 10/04/16  rag 0.0  New - Useful for helping deterine "parent" configId
#-------------------------------------------------------------------------------
def configIdFilter( Type, pattern ) :
  'configIdFilter( Type, pattern ) - Return the (single) configID of the specified type, and filtered by the pattern.'
  result = [ x for x in AdminConfig.list( Type ).splitlines() if x.find( pattern ) > -1 ]
  if len( result ) == 1 :
    result = result[ 0 ]
  else :
    if len( result ) > 1 :
      print '%s() error: too many values (%d).' % ( callerName(), len( result ) )
      print '   Type = "%s"\npattern = "%s"' % ( Type, pattern )
    result = ''
  return result


#-------------------------------------------------------------------------------
# Name: configInfoAsDict()
# Role: Return a dictionary having the primary key being the unique names and
#       and the values being the associated configID for the specified WebSphere
#       Application Server type.
# Note: If no scope (configID) is provided, a name collision may occur when a
#       configuration object name is ambiguous (e.g., server1), in which case,
#       an empty dictionary is returned.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 12/06/28  rag 0.0  Fix - prologue wording change to clarify error conditions
# 11/07/29  rag 0.0  Fix - trivial typographical error in prologue
# 10/04/16  rag 0.0  New - based upon clusterInfo
#-------------------------------------------------------------------------------
def configInfoAsDict( Type, scope = None ) :
  'configInfoAsDict( Type, scope = None ) - Return a dictionary of the specified WebSphere types.'
  result = {}
  funName = callerName()
  #-----------------------------------------------------------------------------
  # Note: If an error/exception occurs, return an empty dictionary.
  #-----------------------------------------------------------------------------
  try :
    #---------------------------------------------------------------------------
    # For each entry, determine its name (if it has one), and add the
    # information to the dictionary result.
    # Note: Passing a scope of None is just like not passing one.
    #---------------------------------------------------------------------------
    for entry in AdminConfig.list( Type, scope ).splitlines() :
      #-------------------------------------------------------------------------
      # is the configID surrounded by quotes?  If so, remove them.
      #-------------------------------------------------------------------------
      if ( entry[ 0 ] == '"' ) and ( entry[ -1 ] == '"' ) :
        name = entry[ 1:-1 ]
      else :
        name = entry
      #-------------------------------------------------------------------------
      # The item name, if it exists, preceeds the opening parenthesis.
      #-------------------------------------------------------------------------
      name = name.split( '(', 1 )[ 0 ]
      if name :
        if result.has_key( name ) :
          raise IndexError( name )
        result[ name ] = entry
  except NameError, e :
    result = {}
    print '%s: Name not found: %s' % ( funName, e )
  except IndexError, e :
    result = {}
    print '%s: Name collision: %s' % ( funName, e )
  except :
    Type, value = sys.exc_info()[ :2 ]
    result = {}
    print '%s: Exception  type: %s' % ( funName, str( Type ) )
    print '%s: Exception value: %s' % ( funName, str( Value ) )
  return result


#-------------------------------------------------------------------------------
# Name: clusterInfo()
# Role: Return a dictionary having the primray key being the unique
#       cluster names, and the values being the associated configID
#       for that cluster
# Example: clusters = clusterInfo()
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/16  rag 0.2  Fix - Rewrite using configInfoAsDict()
# 09/11/14  rag 0.1  Fix - Rewrite using ServerCluster
# 08/10/29  rag 0.0  New - based upon need for createClusterMember.py
#-------------------------------------------------------------------------------
def clusterInfo( scope = None ) :
  'clusterInfo( scope = None ) - Return a dictionary of the cluster members, and their configuration IDs.'
  return configInfoAsDict( 'ServerCluster', scope )


#-------------------------------------------------------------------------------
# Name: configurable
# Role: Return true (1) if wsadmin AdminConfig object is available
#       (0) otherwise
# Note: This can only occur when wsadmin fails to connect to the
#       specified Application Server on the specified/implied port.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/09/29  rag 0.1  Fix - rename "host" to "servers" to more accurately
#                          describe the value being returned.
# 10/05/24  rag 0.0  Add - New, based upon usefulness
#-------------------------------------------------------------------------------
def configurable() :
  'configurable() - Return true (1) if AdminConfig object is available, false (0) otherwise'
  try :
    servers = AdminConfig.list( 'Server' )
    result = 1                         # True  = AdminConfig object is available
  except :
    result = 0                         # False = AdminConfig object not available
  return result


#-------------------------------------------------------------------------------
# Name: displayAttributes
# Role: To display the contents of a dictionary in a more readable format
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/05/20  rag 0.1  Fix - correct prologue block to use correct Name
# 11/04/03  rag 0.0  New - Based upon need
#-------------------------------------------------------------------------------
def displayAttributes( Type ) :
  'displayAttributes( Type ) - Display the attributes for the specified Type'
  if Type in AdminConfig.types().splitlines() :
    text = AdminConfig.attributes( Type ).splitlines()
    attr = [ x.split( ' ', 1 ) for x in text ]
    width = max( [ len( x[ 0 ] ) for x in attr ] )
    for a in attr :
      print '%*s %s' % ( width, a[ 0 ], a[ 1 ] )
  else :
    print 'Unknown Type:', Type


#-------------------------------------------------------------------------------
# Name: displayDict
# Role: To display the contents of a dictionary in a more readable format
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/09/14  rag 0.8  Fix - Handle [] values properly (configIDs with & without blanks)
# 11/05/20  rag 0.7  Add - Test for string, or unicode string...
# 10/09/27  rag 0.6  Add - Add support for nested dictionaries
# 10/05/28  rag 0.5  Fix - Need to check string len before accessing [ 0 ] ...
# 10/05/13  rag 0.4  Fix - Add code to handle double quoted "list" values
# 10/05/12  rag 0.3  Fix - Add try / except in case dict.keys() doesn't exist
#                    Add - New code to display "list" values better
# 10/04/08  rag 0.2  Fix - Handle "empty" dictionary
# 09/11/14  rag 0.1  Fix - Add optional width parm for key values
# 09/04/07  rag 0.0  New - Based upon work for the book
#-------------------------------------------------------------------------------
def displayDict( dict, width = None ) :
  'displayDict( dict, width = None ) - Display dictionary contents in key name order'
  try :
    names = dict.keys()
    names.sort()
    if dict :
      if not width :
        width = max( [ len( x ) for x in names ] )
      for name in names :
        value = dict[ name ]
        if type( value ) == type( '' ) or type( value ) == type( u'' ) :
          if len( value ) > 0 and value[ 0 ] == '[' and value[ -1 ] == ']' and value.count( ' ' ) > 0 :
            print '%*s : [' % ( width, name )
            #-------------------------------------------------------------------
            # Special case: Check for double quoted items.
            # e.g., Config IDs containing embedded blanks.
            #-------------------------------------------------------------------
            if value.find( '"' ) < 0 :
              for item in value[ 1:-1 ].split( ' ' ) :
                print '%*s    %s' % ( width, ' ', item )
            else :
              value = value[ 1:-1 ]      # Remove brackets '[' & ']'
              while value :              # As long as data remains...
                if value[ 0 ] == '"' :   # Is this item double quoted?
                  item, value = value[ 1: ].split( '"', 1 )
                  value = value.lstrip() # Discard any leading blanks
                elif value.find( ' ' ) > -1  :   # Does value have any more blanks?
                  item, value = value.split( ' ', 1 )
                else :                           # Nope, we're done
                  item, value = value, ''
                print '%*s    %s' % ( width, ' ', item )
            print '%*s   ]' % ( width, ' ' )
          else :
            print '%*s : %s' % ( width, name, value )
        elif type( value ) == type( {} ) :
          print '%*s : {' % ( width, name )
          displayDict( value, width + 4 + max( [ len( x ) for x in value.keys() ] ) )
          print '%*s   }' % ( width, ' ' )
        else :
          print '%*s : %s' % ( width, name, `value` )
  except :
    Type, value = sys.exc_info()[ :2 ]
    print '%s() exception:\n  type: %s\n value: %s' % ( callerName(), str( Type ), str( value ) )


#-------------------------------------------------------------------------------
# Name: displayNodeVersions()
# Role: Display the version of each configured node
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/06/20  rag 0.0  New - based upon need
#-------------------------------------------------------------------------------
def displayNodeVersions() :
  "displayNodeVersions() - Display each node name, and it's full version number."
  nodes = [ AdminConfig.showAttribute( n, 'name' ) for n in AdminConfig.list( 'Node' ).splitlines() ]
  nodes.sort()
  width = max( [ len( x ) for x in nodes ] )
  print '\n%*s | Version' % ( width, 'Node' )
  print ( '-' * width ) + '-+-' + ( '-' * 8 )
  for node in nodes :
    print '%*s | %s' % ( width, node, AdminTask.getNodeBaseProductVersion( '[-nodeName %s]' % node ) )
  print


#-------------------------------------------------------------------------------
# Name: displayOperations()
# Role: To display the operations of the specified MBean
# Note: In alphabetical order of function names
#       Dependent upon the fact that Help.operations() returns a
#       header line, and an empty trailing line.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/10/12  rag 0.3  Add - Add "exand" parameter (default false)
# 11/10/12  rag 0.2  Add - Display function parms - 1 per line
# 11/10/12  rag 0.1  Fix - Replace every '[Lsomething;' by 'something[]'
# 11/02/04  rag 0.0  New - Based upon need while writing ISA Lite
#                          Multiple Trace (IMT) scripts
#-------------------------------------------------------------------------------
def displayOperations( bean, expand = 0 ) :
  'displayOperations( bean, expand = 0 ) - Display signature details of specified MBean operations.'
  sortByFunName = lambda x, y: cmp( x[ 1 ].lower(), y[ 1 ].lower() )
  data = []
  for line in re.sub( '\[L([\w.]+);', r'\1[]', Help.operations( bean ) ).splitlines()[ 1:-1 ] :
    result, sign = line.split( ' ', 1 )
    data.append( ( result, sign ) )
  width = max( [ len( x[ 0 ] ) for x in data ] )
  data.sort( sortByFunName )
# for result, sign in data :
#   print '%*s %s' % ( width, result, sign )
  for result, sign in data :
    L, R = sign.find( '(' ), sign.find( ')' )
    if ( L + 1 == R ) or not expand :
      print '%*s %s' % ( width, result, sign )
    else :
      print '%*s %s' % ( width, result, sign[ : L + 1 ] )
      p = sign[ L + 1 : R ].split( ', ' )
      comma = ','
      for i in range( len( p ) ) :
        if i < len( p ) - 1 :
          comma = ','
        else :
          comma = ''
        print ' ' * ( width + L + 2 ), p[ i ] + comma
      print ' ' * ( width + L ), ')'


#-------------------------------------------------------------------------------
#  Name: displayWSASvars()
#  Role: To display the WSAS variables at the specified "scope".
#  Note: This routine ONLY displays the variable at the specific scope, which
#        does not include those defined at a higher configuration level.
# Usage: displayWSASvars( serverName = 'server1' )
#
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/11/30  rag 0.0  New
#-------------------------------------------------------------------------------
def displayWSASvars( cellName = None, nodeName = None, serverName = None ) :
  'displayWSASvars( cellName = None, nodeName = None, serverName = None ) - Display specific WSAS variables.'

  #-----------------------------------------------------------------------------
  # Save the actual name of the called function
  #-----------------------------------------------------------------------------
  funName = callerName()

  #-----------------------------------------------------------------------------
  # overkill? Maybe, especially since we're only expecting one cell to exist
  #-----------------------------------------------------------------------------
  cells = {}
  for cell in AdminConfig.list( 'Cell' ).splitlines() :
    name = AdminConfig.showAttribute( cell, 'name' )
    cells[ name ] = cell

  #-----------------------------------------------------------------------------
  # Was the cellName specified?
  #-----------------------------------------------------------------------------
  if cellName :
    if cells.has_key( cellName ) :
      cell = cells[ cellName ]
    else :
      print '%s() - Error, cell not found: %s' % ( funName, cellName )
      return
  else :
    #---------------------------------------------------------------------------
    # Can we quietly default to the only cell that is present?
    #---------------------------------------------------------------------------
    if len( cells.keys() ) == 1 :
      cellName = cells.keys()[ 0 ]
      cell = cells[ cellName ]
    else :
      cell = AdminConfig.list( 'Cell' ).splitlines()[ 0 ]
      cellName = AdminConfig.showAttribute( cell, 'name' )
      print '%s() - Warning: cellName not specified, using: %s' % ( funName, cellName )

  #-----------------------------------------------------------------------------
  # Build the scope containment path using the specified parameters
  #-----------------------------------------------------------------------------
  path = '/Cell:' + cellName

  #-----------------------------------------------------------------------------
  # Was the nodeName specified?
  #-----------------------------------------------------------------------------
  node = None
  if nodeName :
    nodes = {}
    for node in AdminConfig.list( 'Node', cell ).splitlines() :
      name = AdminConfig.showAttribute( node, 'name' )
      nodes[ name ] = node
    if nodes.has_key( nodeName ) :
      node = nodes[ nodeName ]
      path += '/Node:' + nodeName
    else :
      print '%s() - Error: node not found: %s' % ( funName, nodeName )
      return

  #-----------------------------------------------------------------------------
  # Was the serverName specified?
  # Note: If node == None, the scope is unlimited; beware ambiguity
  #-----------------------------------------------------------------------------
  if serverName :
    servers = {}
    for server in AdminConfig.list( 'Server', node ).splitlines() :
      name = AdminConfig.showAttribute( server, 'name' )
      if servers.has_key( name ) :
        servers[ name ] += '\n' + server
      else :
        servers[ name ] = server
    #---------------------------------------------------------------------------
    # Do any servers with this name exist?
    #---------------------------------------------------------------------------
    if servers.has_key( serverName ) :
      server = servers[ serverName ]
      #-------------------------------------------------------------------------
      # How many servers with this name exist with the specified scope?
      #-------------------------------------------------------------------------
      if len( server.splitlines() ) > 1 :
        print '%s() - Error: ambiguous server specified: %s' % ( funName, serverName )
        return

    #---------------------------------------------------------------------------
    # If the nodeName was unspecified, and the serverName is unambiguous, we 
    # need to find the nodeName to be used by "parsing" the server configID,
    # which should look something like:
    # serverName(cells/cellName/nodes/nodeName/servers/serverName|...)
    #---------------------------------------------------------------------------
    if node == None :
      nodeName = server[ server.find( '(' ) + 1 : server.find( ')' ) ].split( '/' )[ 3 ]
      path += '/Node:' + nodeName

    #---------------------------------------------------------------------------
    # Now we finalize the containment path of the specified server...
    #---------------------------------------------------------------------------
    path += '/Server:' + serverName

  #-----------------------------------------------------------------------------
  # Locate the configID for the user specified scope
  #-----------------------------------------------------------------------------
  scope = AdminConfig.getid( path )

  #-----------------------------------------------------------------------------
  # Build a dictionary of the WAS variables at this scope
  # Note: This does not contain the variable defined only at a higher scope!
  #-----------------------------------------------------------------------------
  vars = {}
  for var in AdminConfig.list( 'VariableSubstitutionEntry', scope ).splitlines() :
    name  = AdminConfig.showAttribute( var, 'symbolicName' )
    value = AdminConfig.showAttribute( var, 'value' )
    vars[ name ] = value

  #-----------------------------------------------------------------------------
  # Sort the variable names & determine the width of the longest name
  #-----------------------------------------------------------------------------
  names = vars.keys()
  names.sort()
  width = max( [ len( n ) for n in names ] )

  #-----------------------------------------------------------------------------
  # Display the names, in sorted order
  #-----------------------------------------------------------------------------
  width = max( width, 10 )
  print '%s | %s' % ( 'Variable'.center( width ), 'Value ' )
  print '%s-+-%s' % ( '-' * width, '-' * 25 )
  for name in names :
    print '%*s | %s' % ( width, name, vars[ name ] )


#-------------------------------------------------------------------------------
#  Name: firstNamedConfigType()
#  Role: To return the first configId of the resource of the specified
#        Type having the specified attribute value.
#  Note: Passing a scope of None is just like not specifying one.
#        Default value of attr is "name"
#
# Usage: import WAuJ_utilities as WAuJ
#        ...
#        name   = 'server1'
#        server = WAuJ.firstNamedConfigType( 'Server', name )
#        if server :
#          # Do something with server resource
#          ...
#        else :
#          print 'Server not found, name = "%s".' % name
#
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/06/24  rag 0.1  Fix - Renamed from findNamedConfigType
#                        - Changed parameter order to put Type first.
#                        - Rewritten to use findScopedTypes()
#                        - Usage example provide in comment block
# 10/04/22  rag 0.0  New
#-------------------------------------------------------------------------------
def firstNamedConfigType( Type, value, scope = None, attr = None ) :
  'firstNamedConfigType( Type, value, scope = None, attr = None ) - Return the first configId of the given Type having specified attribute value.'
  items = findScopedTypes( Type, value, scope, attr )
  if len( items ) :
    result = items[ 0 ]
  else :
    result = None
  return result


#-------------------------------------------------------------------------------
#  Name: findScopedTypes()
#  Role: Return the list of configuration IDs for resources of the
#        specified Type having a given attribute value, with an
#        optional scope.
#  Note: Passing a scope of None is just like not specifying one.
#      - Default value of attr is "name"
#      - List comprehension makes this really easy, but harder to read.
#      - This routine returns a list of all matching configIds.
#
# Usage: import WAuJ_utilities as WAuJ
#        ...
#        name    = 'server1'
#        servers = WAuJ.findScopedTypes( 'Server', name )
#        if len( servers ) > 1 :
#          print 'Server (name = "%s") is ambiguous.' % name
#
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/05/13  rag 0.1  Fix - corrected prologue comment block to use the
#                          proper function name.
# 10/06/24  rag 0.0  New
#-------------------------------------------------------------------------------
def findScopedTypes( Type, value, scope = None, attr = None ) :
  'findScopedTypes( Type, value, scope = None, attr = None ) - Return the list of configIds of the given Type having specified attribute value.'
  if not attr :
    attr = 'name'
  return [ x for x in AdminConfig.list( Type, scope ).splitlines() if AdminConfig.showAttribute( x, attr ) == value ]


#-------------------------------------------------------------------------------
# Name: findTypes()
# Role: Returns the list of configuration types that containing the
#       specified text.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/06/04  rag 0.0  New - based upon usefulness
#-------------------------------------------------------------------------------
def findTypes( text ) :
  'findTypes( text ) - Returns the list of configuration types that containing the specified text.'
  result = []
  for Type in AdminConfig.types().splitlines() :
    if Type.find( text ) > -1 :
      result.append( Type )
  return result


#-------------------------------------------------------------------------------
# Name: fixFileName()
# Role: Unfortunately, an ugly "wart" exists when dealing with Windows
#       fileNames.  Specifically, some Windows fileNames, when passed
#       into a wsadmin script can inadvertently cause "correct"
#       filename characters to be misinterpreted as special Jython
#       "escape" characters.  This occurs when the filename, or
#       directory name character that occur immediately after a
#       directory delimiter (i.e., '\\') happen to be one of the
#       "special" Jython escape characters.  Instead of correctly
#       identifying the directory delimiter as '\\', and leaving the
#       subsequent character alone, the directory delimiter and the
#       character that follows are interpreted as one of these
#       "special" Jython escape character.  So, the purpose of this
#       routine is to correct that interpretation error.
# Note: This routine is equivalent to:
#       def fixFileName( fileName ) :
#         result = fileName.replace( '\a', r'\a' )
#         result = result.replace( '\b', r'\b' )
#         result = result.replace( '\f', r'\f' )
#         result = result.replace( '\n', r'\n' )
#         result = result.replace( '\r', r'\r' )
#         result = result.replace( '\t', r'\t' )
#         result = result.replace( '\v', r'\v' )
#         return result
#-------------------------------------------------------------------------------
def fixFileName( fileName ) :
  'fixFileName( filename ) - Return the specified string with selected escape characters unescaped.'
  return fileName.replace(
    '\a', r'\a' ).replace(
    '\b', r'\b' ).replace(
    '\f', r'\f' ).replace(
    '\n', r'\n' ).replace(
    '\r', r'\r' ).replace(
    '\t', r'\t' ).replace(
    '\v', r'\v' )


#-------------------------------------------------------------------------------
# Name: fullSync
# Role: Locate all of the active nodeagents, and synchronize each
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/06/03  rag 0.1  Fix - rewrite to use DM syncActiveNodes() method
# 11/04/27  rag 0.0  New - For ISA-Lite
#-------------------------------------------------------------------------------
def fullSync() :
  'fullSync() - Synchronize the active nodes'
  funName = callerName()

  #-----------------------------------------------------------------------------
  # To perform a synchronization, we need to be connected to a DM...
  #-----------------------------------------------------------------------------
  dm = AdminControl.completeObjectName( 'type=DeploymentManager,*' )
  if dm :
    nodes = AdminControl.invoke( dm, 'syncActiveNodes', 'true' )
    nodes = ', '.join ( nodes.splitlines() )
    print '%s(): synchronized nodes: %s' % ( funName, nodes )
  else :
    print '%s(): Synchronization not possible without an active Deployment Manager.' % funName


#-------------------------------------------------------------------------------
# Name: getEndPointName()
# Role: Return the name of the configured EndPoint for the given port
#       on the specified server (or '' if the port is not configured).
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/22  rag 0.0  New
#-------------------------------------------------------------------------------
def getEndPointName( port, serverName, nodeName = None ) :
  'getEndPointName( port, serverName, nodeName = None ) - Return the name of the configured EndPoint for the given port on the specified server.'
  if type( port ) == type( 0 ) :
    port = `port`                      # Ensure that the port number is a string
  return getPorts( serverName, nodeName ).get( port, '' )


#-------------------------------------------------------------------------------
# Name: getEndPoints()
# Role: Return a dictionary, indexed by endPoint names, of the ports
#       configured for the specified server.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/22  rag 0.0  New
#-------------------------------------------------------------------------------
def getEndPoints( serverName, nodeName = None ) :
  'getEndPoints( serverName, nodeName = None ) - Return a dictionary of the configured EndPoints for the specified server.'
  result = {}
  #-----------------------------------------------------------------------------
  # If a nodeName is specified, use it to limit the search scope.
  #-----------------------------------------------------------------------------
  if nodeName :
    scope = firstNamedConfigType( 'Node', nodeName  )
  else :
    scope = None
  #-----------------------------------------------------------------------------
  # Locate the named (and optionally scoped) 'ServerEntry'
  #-----------------------------------------------------------------------------
  serverEntry = firstNamedConfigType( 'ServerEntry', serverName, scope, 'serverName' )
  if serverEntry :
    #---------------------------------------------------------------------------
    # for each NamedEndPoint on this server...
    #---------------------------------------------------------------------------
    for namedEndPoint in AdminConfig.list( 'NamedEndPoint', serverEntry ).splitlines() :
      Name = AdminConfig.showAttribute( namedEndPoint, 'endPointName' )
      epId = AdminConfig.showAttribute( namedEndPoint, 'endPoint' )
      result[ Name ] = AdminConfig.showAttribute( epId, 'port' )
  #-----------------------------------------------------------------------------
  # Return either an empty dictionary, or one indexed by EndPointNames,
  # containing the associated port numbers.
  #-----------------------------------------------------------------------------
  return result


#-------------------------------------------------------------------------------
# Name: getPort()
# Role: Return the configured Port number for the specified (named)
#       EndPoint on the specified server.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/22  rag 0.0  New
#-------------------------------------------------------------------------------
def getPort( endPointName, serverName, nodeName = None ) :
  'getPort( endPointName, serverName, nodeName = None ) - Return the configured Port number for the specified (named) EndPoint on the the specified server.'
  return getEndPoints( serverName, nodeName ).get( endPointName, '' )


#-------------------------------------------------------------------------------
# Name: getPorts()
# Role: Return a dictionary, indexed by port number, of the named
#       EndPoints for the specified server.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/22  rag 0.0  New
#-------------------------------------------------------------------------------
def getPorts( serverName, nodeName = None ) :
  'getPorts( serverName, nodeName = None ) - Return a dictionary, indexed by port number, of the named EndPoints for the specified server.'
  result    = {}
  endPoints = getEndPoints( serverName, nodeName )
  for name, port in endPoints.items() :
    result[ port ] = name
  return result


#-------------------------------------------------------------------------------
# Name: localMode
# Role: Return true (1) if wsadmin is running in "local mode", false
#       (0) otherwise
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 09/11/15  rag 0.0  Add - New, based upon usefulness
#-------------------------------------------------------------------------------
def localMode() :
  'localMode() - Return true (1) if executing in "local" mode, false (0) otherwise'
  try :
    host   = AdminControl.getHost()
    result = 0                         # False = we are connected
  except :
    result = 1   # True  = AdminControl service not available
  return result


#-------------------------------------------------------------------------------
# Name: MBattrAsDict
# Role: Utility routine used to return a dictionary of attributes for
#       the specified mbean
# Note: Depends upon availability of WSAS Admin Objects via sys.modules
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/04/27  rag 0.2  Del - Remove "import Help, AdminControl", since
#                          this is done for us at the end of the file.
# 09/11/10  rag 0.1  Add - Add 'Modifiable' value to result
# 09/04/08  rag 0.0  New - insight obtained while writing the book
#-------------------------------------------------------------------------------
def MBattrAsDict( mbean ) :
  "MBattrAsDict( mbean ) - Given an MBean string, return a dictionary of it's attributes."
  funName = callerName()               # Name of this function
  result = {}                          # Result is a dictionary
  #-----------------------------------------------------------------------------
  # The first line of Help.attributes() result contains the "column
  # headings", not values, and is ignored by slicing using [ 1: ].
  # For each valid attribute, we use the name to get the value
  #-----------------------------------------------------------------------------
  try :                                # Be prepared for an error
#   import Help, AdminControl          # Get access to WSAS objects
    attr = Help.attributes( mbean ).splitlines()[ 1: ]
    for att in attr :
      name = att.split( ' ', 1 )[ 0 ]  # Everything ahead of 1st space
      #-------------------------------------------------------------------------
      # Unfortunately, for some attribute names, an attempt to
      # getAttribute() will cause an exception, these we ignore.
      #-------------------------------------------------------------------------
      try :
        result[ name ] = AdminControl.getAttribute( mbean, name )
      except :
        pass
    #---------------------------------------------------------------------------
    # After all available attributes have been retrieved, see if one
    # name "Modifiable" exists.  If it does, we have a problem, which
    # needs to be reported.
    # Otherwise, use list comprehension to locate those attributes
    # that are specified as "Read-Write".  Put all of these attribute
    # names into a list, and save it as result[ 'Modifiable' ].
    #---------------------------------------------------------------------------
    # Note: Specifying x.split( ' ', 1 )[ 0 ] means that a maximum of
    #       1 split will occur (i.e., strings will be created), and
    #       only the first (i.e., the leading non-blank characters)
    #       will be returned.
    #---------------------------------------------------------------------------
    if result.has_key( 'Modifiable' ) :
      print '%(funName)s: "Modifiable" attribute already exists, and not replace.' % locals()
    else :
      result[ 'Modifiable' ] = [ x.split( ' ', 1 )[ 0 ] for x in attr if x.endswith( 'RW' ) ]
  except :
    notavail = 'AdminControl service not available'
    #---------------------------------------------------------------------------
    # One likely source of errors is that an invalid MBean was
    # provided, in which case an empty dictionary is returned.
    #---------------------------------------------------------------------------
    ( kind, value ) = sys.exc_info()[ :2 ]
    ( kind, value ) = str( kind ), str( value )
    if value.endswith( notavail ) :
      if 'AdminTask' in sys.modules.keys() :
        print '%(funName)s "%(notavail)s": Was wsadmin started with "-conntype none"?' % locals()
      else :
        print '%(funName)s "%(notavail)s": wsadmin isn\'t connected to a server.' % locals()
    elif value.find( 'WASX7025E' ) > -1 :
      print '%(funName)s: Invalid mbean identifier: %(mbean)s' % locals()
    else :
      print 'Exception  type: ' + kind
      print 'Exception value: ' + value
  return result


#-------------------------------------------------------------------------------
# Name: MBnameAsDict
# Role: Utility routine used to return a dictionary of name/value
#       details from an MBean name
# Note: Exception handler requires sys module
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 08/10/27  rag 0.1  Fix - Minor code cleanup
# 08/09/17  rag 0.0  New - insight obtained while writing the book
#-------------------------------------------------------------------------------
def MBnameAsDict( beanName ) :
  'MBnameAsDict( beanName ) - Given an MBean name, return a dictionary of its name/value components.'
  funName = callerName()               # Name of this function
  domain  = 'WebSphere:'               # MBean name prefix
  result  = {}                         # Result is a dictionary
  try :                                # Be prepared for an error
    #---------------------------------------------------------------------------
    # Verify that we are working with a WebSphere MBean
    #---------------------------------------------------------------------------
    if beanName.startswith( domain ) :
      #-------------------------------------------------------------------------
      # The rest of MBean name should be composed of comma separated
      # name=value pairs.
      #-------------------------------------------------------------------------
      for field in beanName[ len( domain ): ].split( ',' ) :
        ( name, value ) = field.split( '=', 1 )
        result[ name ] = value
    else :
      print '''%(funName)s:
Warning: Specified MBean name doesn\'t start with "%(domain)s" and is ignored.
  MBean name: "%(beanName)s"''' % locals()
  except :
    ( kind, value ) = sys.exc_info()[ :2 ]
    print '''%(funName)s: Unexpected exception.\n
  Exception  type: %(kind)s
  Exception value: %(value)s''' % locals()
  return result


#-------------------------------------------------------------------------------
# Name: memberInfo()
# Role: Return a dictionary with the primary key being the unique cluster member
#       name, and the value being the associated configID for that member.
# Note: Member names can be ambiguous, just like server names.  In this case,
#       care must be used to use the node name to qualify the member.
#       ***** Warning *****
#       This code does NOT do that, if an ambiguous member name occurs, an
#       error message is displayed by configInfoAsDict(), and an empty
#       dictionary is returned.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 12/06/28  rag 0.0  Fix - prologue comment / warning about ambiguous names
# 10/04/16  rag 0.0  New - Write using configInfoAsDict()
#-------------------------------------------------------------------------------
def memberInfo( scope = None ) :
  'memberInfo( scope = None ) - Return a dictionary of the cluster member names, and their configuration IDs.'
  return configInfoAsDict( 'ClusterMember', scope )


#-------------------------------------------------------------------------------
# Name: nodeInfo()
# Role: Return a dictionary having the primary key being the unique
#       node names, and the values being the associated configID
#       for each node.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/16  rag 0.0  New - Write using configInfoAsDict()
#-------------------------------------------------------------------------------
def nodeInfo( scope = None ) :
  'nodeInfo( scope = None ) - Return a dictionary of the node names, and their configuration IDs.'
  return configInfoAsDict( 'Node', scope )


#-------------------------------------------------------------------------------
# Name: nvListAsDict()
# Role: To display the contents of a dictionary in a more readable format
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 09/11/15  rag 0.1  Add - docstring
# 09/08/18  rag 0.0  New - see stringAsNestedList()
#-------------------------------------------------------------------------------
def nvListAsDict( nvList ):
  'nvListAsDict( mvList ) - Convert a list containing name/value pairs into a dictionary'
  result = {}
  for name, value in nvList :
    result[ name ] = value
  return result


#-------------------------------------------------------------------------------
# Name: nvTextListAsDict
# Role: Convert a list of name/value pairs found in the specified text
#       string into a dicationary.
# Note: Depends upon availability of WSAS Admin Objects via sys.modules
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/01/27  rag 0.5  Fix - Change "cmdName" to "funName"
# 09/11/15  rag 0.4  Add - docstring
# 09/04/07  rag 0.3  Add - Added displayDict() call to example
# 09/03/21  rag 0.2  Add - Add "role" description & corrected example
# 08/12/18  rag 0.1  Fix - Handle "no value" pair (e.g., "[nodeShortName ]")
# 08/12/17  rag 0.0  New - Based upon work for book
#-------------------------------------------------------------------------------
# Example use:
# > from WAuJ_utilities import nvTextListAsDict, displayDict
# > sDict = nvTextListAsDict( AdminTask.showServerTypeInfo( 'APPLICATION_SERVER' ) )
# > displayDict( sDict )
#-------------------------------------------------------------------------------
def nvTextListAsDict( text ) :
  'nvTextListAsDict( text ) - Convert a list of name/value pairs into a dictionary.'
  funName = callerName()
  #-----------------------------------------------------------------------------
  # Initialize the dictionary to be returned
  #-----------------------------------------------------------------------------
  result = {}
  #-----------------------------------------------------------------------------
  # Verify that the specified string "looks" right...
  #-----------------------------------------------------------------------------
  if ( text.count( '[' ) == text.count( ']' ) ) and ( text[ 0 ] == '[' ) and ( text[ -1 ] == ']' ) :
    #---------------------------------------------------------------------------
    # Remove outer brackets (i.e., '[]') and then leading/trailing blanks
    #---------------------------------------------------------------------------
    innerText = text[ 1:-1 ].strip()
    #---------------------------------------------------------------------------
    # Locate a possible unused character so the list of values can
    # easily be split into name value pairs
    #---------------------------------------------------------------------------
    delimiters = ',.|!@#'              # Possible delimiter values
    for delim in delimiters :
      #-------------------------------------------------------------------------
      # If this char (delim) doesn't exist in the string, put it in,
      # between the close and open brackets so that it can be used to
      # split the line into a list of strings like '[name value]'.
      #-------------------------------------------------------------------------
      if innerText.count( delim ) == 0 :
        for pair in innerText.replace( '] [', ']%s[' % delim ).split( delim ) :
          #---------------------------------------------------------------------
          # verify that the string starts and ends with brackets...
          # Note: a == b == c is only true if both a == b and b == c
          #---------------------------------------------------------------------
          if ( pair.count( '[' ) == pair.count( ']' ) == 1 ) and ( pair[ 0 ] == '[' ) and ( pair[ -1 ] == ']' ) :
            #-------------------------------------------------------------------
            # Occasionally, we have a situation where pair contains
            # only a name, and not a name/value pair.
            # So, this code was added to handle that rare situation.
            #-------------------------------------------------------------------
            contents = pair[ 1:-1 ].strip()
            try :
              ( name, value ) = contents.split( ' ', 1 )
            except :
              ( name, value ) = ( contents, '' )
            result[ name ] = value
          else :
            print '%s error - Unexpected text: "%s" (ignored).' % ( funName, pair )
        #-----------------------------------------------------------------------
        # All name/pair sub-strings have been processed, we're done
        #-----------------------------------------------------------------------
        break
    else :
      print '%s error - Unable to split data, empty dictionary returned.' % funName
      return {}
  else :
    print '%s error - Unexpected data format: "%s", empty dictionary returned.' % ( funName, text )
  return result

#-------------------------------------------------------------------------------
# Name: parentTypes()
# Role: Return a multi-line string (i.e., containing newline separators) of all
#       of the valid parent types for the specified configuration type.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 12/05/18  rag 0.0  New
#-------------------------------------------------------------------------------
def parentTypes( Type, WSAStypes = None ) :
    import os.linesep as newline
    #---------------------------------------------------------------------------
    # Local optimization - minimize the number of calls to AdminConfig.types()
    #---------------------------------------------------------------------------
    if not WSAStypes :
        WSAStypes = AdminConfig.types().splitlines()
    #---------------------------------------------------------------------------
    # Use AdminConfig.parents() if we can, otherwise figure it out for ourself
    #---------------------------------------------------------------------------
    if Type in WSAStypes :
        result = AdminConfig.parents( Type )
        if result.startswith( 'WASX7351I' ) :
            result = newline.join( [ kind for kind in WSAStypes if AdminConfig.attributes( kind ).find( Type ) > -1 ] )
    else :
        print 'parentTypes() error: unknown / unrecognized type:', Type
        result = None
    return result

#-------------------------------------------------------------------------------
# Name: scopeAsDict
# Role: Convert the specified scope configuration object into a dictionary
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/09/27  rag 0.1  Add - Include scopeName & scopeType values in result
# 10/09/24  rag 0.0  New - Based upon work down for certZilla
#-------------------------------------------------------------------------------
# Example use:
# > from WAuJ_utilities import WAuJ
# > ks    = AdminTask.listKeyStores( '[-all true]' ).splitlines()[ 0 ]
# > attr  = WAuJ.showAsDict( ks )
# > scope = WAuJ.scopeAsDict( attr[ 'managementScope' ] )
#-------------------------------------------------------------------------------
def scopeAsDict( configId ) :
  'scopeAsDict( configId ) - Return a dictionary of the specified scope config object.'
  funName = callerName()
  result = {}
  try :
    result = showAsDict( configId )
    Name = result[ 'scopeName' ]
    result.update( scopeNameAsDict( Name ) )
    result[ 'configId' ] = configId
    result[ 'name'     ] = result[ result[ 'scopeType' ] ]
  except :
    Type, value = sys.exc_info()[ :2 ]
    print '%s exception  Type: %s\n\tvalue: %s' % ( funName, str( Type ), str( value ) )
  return result


#-------------------------------------------------------------------------------
# Name: scopeNameAsDict
# Role: Convert specified scopeName string into a dictionary
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/09/24  rag 0.0  New - Based upon work down for certZilla
#-------------------------------------------------------------------------------
# Example use:
# > from WAuJ_utilities import WAuJ
# > ks    = AdminTask.listKeyStores( '[-all true]' ).splitlines()[ 0 ]
# > attr  = WAuJ.showAsDict( ks )
# > info  = WAuJ.showAsDict( attr[ 'managementScope' ] )
# > scope = WAuJ..scopeNameAsDict( info[ 'scopeName' ] )
#-------------------------------------------------------------------------------
def scopeNameAsDict( scopeName ) :
  'scopeNameAsDict( scopeName ) - Return a dictionary of the specified scopeName.'
  funName = callerName()
  result = {}
  try :
    nv = scopeName.split( ':' )
    if len( nv ) % 2 :
       raise ValueError, '%s error: Unrecognized input: %s' % ( funName, scopeName )
    for i in range( 0, len( nv ), 2 ) :
      n, v = nv[ i ], nv[ i + 1 ]
#     print '%s() name="%s" value="%s"' % ( funName, n[ 1:-1 ], v )
      result[ n[ 1:-1 ] ] = v
  except :
    print '%s exception: %s' % ( funName, str( sys.exc_info()[ 1 ] ) )
    result = {}
  return result


#-------------------------------------------------------------------------------
# Name: scopedWSASvariables()
# Role: Return a dictionary of the specific WebSphere Application
#       Server (WSAS) variables scoped by the specified configId.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/05/19  rag 0.2  Fix handle KeyError for VMdict[ 'entries' ]
#                    Fix handle empty VMid
# 10/04/22  rag 0.1  Add docstring
# 10/04/18  rag 0.0  New
#-------------------------------------------------------------------------------
def scopedWSASvariables( configId ) :
  'scopedWSASvariables( configId ) - Return a dictionary of the WSAS variables scoped by the specified configId.'
  funName = callerName()
  start = configId.find( '(' )
  if start < 0 :
    print '%s() error - no \'(\' found in configId: "%s"' % ( funName, configId )
    return
  fini = configId.find( '|' )
  if fini < 0 :
    print '%s*( error - no \'|\' found in configId: "%s"' % ( funName, configId )
    return
  #-----------------------------------------------------------------------------
  # Quick and easy extraction of the part of the configId we need to
  # filter the VariableMap configuration items.
  #-----------------------------------------------------------------------------
  prefix = configId[ start : fini + 1 ]
  VMid = configIdFilter( 'VariableMap', prefix )
  #-----------------------------------------------------------------------------
  # Use this VariableMap configId to determine which entries exist.
  #-----------------------------------------------------------------------------
  result = {}
  if VMid :
    VMdict = showAsDict( VMid )
    entries = VMdict.get( 'entries', '[]' )[ 1:-1 ]
    #---------------------------------------------------------------------------
    # If the list of entry configIds is not empty, extrct the details.
    #---------------------------------------------------------------------------
    if entries :
      for entry in entries.split( ' ' ) :
#       print 'entry:', entry
        entryDict = showAsDict( entry )
        result[ entryDict[ 'symbolicName' ] ] = entryDict[ 'value' ]
  return result


#-------------------------------------------------------------------------------
# Name: serverInfo()
# Role: Return a dictionary having the primary key being the unique
#       server name, and the value being the associated configID for
#       that server.
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 10/04/16  rag 0.0  New - Write using configInfoAsDict()
#-------------------------------------------------------------------------------
def serverInfo( scope = None ) :
  'serverInfo( scope = None ) - Return a dictionary of the server names, and their configuration IDs.'
  return configInfoAsDict( 'Server', scope )


#-------------------------------------------------------------------------------
# Name: showAsDict
# Role: Convert result of AdminConfig.show( configID ) to a dictionary
# Note: Depends upon availability of WSAS Admin Objects via sys.modules
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/04/27  rag 0.2  Del - Remove "import AdminConfig", since this is
#                          done for us at the end of the file.
# 09/08/08  rag 0.1  Fix - remove quotes of value
# 08/09/06  rag 0.0  New - Based upon work down for IMPACT 2008
#-------------------------------------------------------------------------------
# Example use:
# > from WAuJ_utilities import showAsDict
# > servers = AdminConfig.list( 'Server' ).splitlines()
# > svrDict = showAsDict( servers[ 0 ] )
#-------------------------------------------------------------------------------
def showAsDict( configId ) :
  'showAsDict( configId ) - Return a dictionary of the AdminConfig.show( configID ) result.'
  result = {}
  try :
#   import AdminConfig                 # Get access to WSAS objects
    #---------------------------------------------------------------------------
    # The result of the AdminConfig.show() should be a string
    # containing many lines.  Each line of which starts and ends
    # with brackets.  The "name" portion should be separated from the
    # associated value by a space.
    #---------------------------------------------------------------------------
    for item in AdminConfig.show( configId ).splitlines() :
      if ( item[ 0 ] == '[' ) and ( item[ -1 ] == ']' ) :
        ( key, value ) = item[ 1:-1 ].split( ' ', 1 )
        if ( value[ 0 ] == '"' ) and ( value[ -1 ] == '"' ) :
          value = value[ 1:-1 ]
        result[ key ] = value
  except NameError, e :
    print 'Name not found: ' + str( e )
  except :
    ( kind, value ) = sys.exc_info()[ :2 ]
    print 'Exception  type: ' + str( kind )
    print 'Exception value: ' + str( value )
  return result


#-------------------------------------------------------------------------------
# Name: stringAsNestedList()
# Role: Parse / convert a "well formed" input string into a nested
#       list using a very simple Finite State Machine (FSM) and stack
#       so recursive descent isn't needed.
#
# States
#   -1 : Finished
#    0 : Looking for brackets
#    1 : collecting characters
#
# Finite State machine (FSM)
#
#        +-----+-----+-----+
# States | -1  |  0  |  1  |
#        +=====+=====+=====+
#   '['  |     |  A  |     |
#        +-----+-----+-----+
#   ']'  |     |  B  |  E  |
#        +-----+-----+-----+
#   ' '  |     |  -  |  D  |
#        +-----+-----+-----+
#  other |     |  C  |     |
#        +-----+-----+-----+
#
# Actions:
#    A | Current_List = []      Push( Current_List ) onto our stack
#    B | Complete Current_List; Pop TOS; Append Current_List to TOS
#    C | Start saving characters
#    D | Previous "word" complete.  Save it.
#    E | Handle closing bracket
#    F | Save current character
#    - | Ignore
#
# Note: TOS == Top of Stack
#
# Example:
#   > import WAuJ_utilities as WAuJ
#   > ssText = AdminTask.getActiveSecuritySettings()   # New in 7.0
#   > ssNL   = WAuJ.stringAsNestedList( ssText )
#   > ssDict = WAuJ.nvListAsDict( ssNL )
#
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 09/11/15  rag 0.1  Add - docstring
# 09/08/18  rag 0.0  New - based upon need
#-------------------------------------------------------------------------------
def stringAsNestedList( str ) :
  'stringAsNestedList( str ) - Convert a well formed nested string list into a nested list of strings'
  str    = str.replace( '\r', '' )     # Remove all Carriage Return
  str    = str.replace( '\n', '' )     #    ... and Line Feed chars
  result = []                          # initialize as an empty list
  state  = 0                           # Looking for brackets
  lst    = None                        # Current list
  lstStr = None                        # Collecting string
  #-----------------------------------------------------------------------------
  # Loop through all the characters in the input string
  #-----------------------------------------------------------------------------
  for c in str :                       #
    if state == 0 :                    # State <- Looking for bracket
      if c == '[' :                    # Start a new list
        lst = []                       # Initialize "current" list
        result.append( lst )           # Push onto the stack
      elif c == ' ' :                  #
        pass                           # Ignore blanks between brackets
      elif c == ']' :                  #
        if len( lst ) == 1 :           # Does list contain only 1 element?
          lst.append( '' )             #   Append implied empty value.
        #-----------------------------------------------------------------------
        # Get the just-built list of the level (lst) and append it
        # to the parent list.
        #-----------------------------------------------------------------------
        result.pop()                   # Remove current lst from TOS
        if len( result ) > 0 :         #
          result[ -1 ].append( lst )   # Append to the TOS, which
          lst = result[ -1 ]           # becomes the current list
        else :                         #
          result.append( lst )         # We should be done now
          state = -1                   # State <- Finished
      else :                           #
        lstStr = [ c ]                 # First character to be collected
        state = 1                      # State <- collecting characters
    elif state == 1 :                  # Collecting characters
      if c == ' ' :                    # Delimiter?
        lst.append( ''.join( lstStr ) )  # Collected characters => string
        state = 0                      # State <- "Looking for bracket"
      elif c == ']' :                  #
        lst.append( ''.join( lstStr ) )  # Collected string
        #-----------------------------------------------------------------------
        # Get the just-built list of the level (lst) and append it
        # to the parent list.
        #-----------------------------------------------------------------------
        result.pop()                   # remove lst from TOS
        if len( result ) > 0 :         #
          result[ -1 ].append( lst )   # Append to the upper level, which
          lst = result[ -1 ]           # becomes the current list from
          state = 0                    # State <- "Looking for bracket"
        else :                         #
          result.append( lst )         # We should be done now
          state = -1                   # State <- Finished
      else :                           #
        lstStr.append( c )             # Save the current character
    elif state == -1 :                 # Finished?
      return result[ 0 ]               #
  if state == -1 :                     #
    assert len( result ) == 1          #
    return result[ 0 ]                 #
  else :                               #
    print 'stringAsNestedList() Unexpected Error.'
    print '  state:', state            #
    print ' result:', repr( result )   #
    print '    lst:', repr( lst )      #
    print ' lstStr:', repr( lstStr )   #
    return None                        #


#-------------------------------------------------------------------------------
# Name: stringListAsList
# Role: Convert a string list into a list of strings.
# Note: Convenient for converting a list of configuaration IDs (any of
#       which may be surrounded by quotes).
# Note: Any surrounding quotes are removed from the list entries
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 09/11/15  rag 0.1  Fix - Last entry doesn't have to have quotes
#                    Add - docstring
# 09/11/14  rag 0.0  New - Based upon word done with cluster members
#-------------------------------------------------------------------------------
# Example use:
# > import WAuJ_utilities as WAuJ
# > clusters = WAuJ.clusterInfo()
# > for cluster in clusters.keys() :
# >   clustDict = WAuJ.showAsDict( clusters[ cluster ] )
# >   print cluster
# >   for member in WAuJ.stringListAsList( clustDict[ 'members' ] ) :
# >     print '  %s : %s' % ( member.split( '(', 1 )[ 0 ], member )
#-------------------------------------------------------------------------------
def stringListAsList( str ) :
  'stringListAsList( str ) - Convert an unnested string list into a list of strings'
  result = []
  funName = callerName()
  if str and str[ 0 ] == '[' and str[ -1 ] == ']' :
    str = str[ 1:-1 ] + ' '       # Guarantee trailing space
    try :
      #-------------------------------------------------------------------------
      # While string contains data
      #-------------------------------------------------------------------------
      while str :
        #-----------------------------------------------------------------------
        # Does string start with a double quote?
        #-----------------------------------------------------------------------
        if str[ 0 ] == '"' :
          qIdx = str.find('"',1)
          pIdx = str.find(')',1)
          if pIdx > qIdx:
            ( val, str ) = str.split( ' ', 1 )
            result.append( val )
          else:
            ( val, str ) = str[ 1: ].split( '"', 1 )
            result.append( val )
        #-----------------------------------------------------------------------
        # Does string start with a space?
        #-----------------------------------------------------------------------
        elif str[ 0 ] == ' ' :
          str = str[ 1: ]
        #-----------------------------------------------------------------------
        # Next delimiter is a space (if one exists).
        #-----------------------------------------------------------------------
        else :
          ( val, str ) = str.split( ' ', 1 )
          result.append( val )
    except NameError, e :
      print '%s: Name not found: %s' % ( funName, str( e ) )
    except :
      ( kind, value ) = sys.exc_info()[ :2 ]
      print '''%(funName)s: Unexpected error:
  Exception  type: %(kind)s
  Exception value: %(value)s''' % locals()
  else :
    print '%s: Unexpected data format.  Missing []' % funName
  return result


#-------------------------------------------------------------------------------
# Name: unravel()
# Role: Use the specified resource configId (of a Server, Node, Cell,
#       ServerCluster, or ClusterMember), to resolve the value of the
#       specified WSAS variable.
# Note: To resolve, or completely "unravel" a string containing WSAS
#       variable references, we need to first obtain a dictionary of
#       the variables that exist for this context (e.g., for a specific
#       AppServer).
# e.g.: wsadmin>import WAuJ_utilities as WAuJ 
#       wsadmin>server   = AdminConfig.list( 'Server' ).splitlines()[ -1 ] 
#       wsadmin>ts       = AdminConfig.list( 'TraceService', server ) 
#       wsadmin>tsDict   = WAuJ.showAsDict( ts ) 
#       wsadmin>tl       = tsDict[ 'traceLog' ] 
#       wsadmin>tlDict   = WAuJ.showAsDict( tl ) 
#       wsadmin>tracelog = tlDict[ 'fileName' ]      # ${SERVER_LOG_ROOT}/trace.log
#       wsadmin>print WAuJ.unravel( tracelog, server ) 
#       C:\IBM\WebSphere\AppServer70\profiles\AppSrv01/logs/server1/trace.log
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 13/05/04  rag 0.5  Add - (optional) subParens parameter to allow $() to be
#                          substituted as well since StreamRedirect fileName
#                          attributes use $() instead of ${}
#                    Add - (optional) quiet parameter to silently work around
#                          known defect
# 11/06/03  rag 0.4  Fix - Correct code that checks for specific "unknown"
#                          variables: SERVER, and CELL 
# 11/05/02  rag 0.3  Add - special check for ${SERVER} on a NODE_AGENT server type
# 11/04/30  rag 0.2  Fix - Use string.replace() instead of re.sub()
# 10/04/19  rag 0.1  Fix - Check for (and handle) '[]' (empty WSAS variable values)
# 10/04/18  rag 0.0  New
#-------------------------------------------------------------------------------
def unravel( value, configId, subParens = 0, quiet = 0 ) :
  '''unravel( value, configId, subParens = 0, quiet = 0 )
  - Complete variable substitution of specified value, using specified scoping configId.
    subParens == 1  Indicates that $() should be treated as ${}, and
    quiet     == 1  Indicates that warning messages should not be displayed.
  '''
  funName = callerName()               # Name of current routine
  variables = WSASvariables( configId )
  #-----------------------------------------------------------------------------
  # If the user wants $() treated like ${}, then subParens should be "true"
  #-----------------------------------------------------------------------------
  if subParens :
    value = value.replace( '(', '{' ).replace( ')', '}' )
  var = re.compile( '\${(\w+)}' )      # Find a valid variable
  while value.find( '${' ) > -1 :      # Does it look like one exists?
    mo = var.search( value )           # Match Object (mo)
    if mo :                            # One exists
      name = mo.group( 1 )             # Named variable e.g., "${NAME}" => 'NAME'
      if not variables.has_key( name ) :
        cDict = showAsDict( configId ) # Check for a specific / known "defect"
        if name == 'SERVER' :          #   i.e., ${SERVER} on a nodeagent
          if cDict[ 'serverType' ] == 'NODE_AGENT' :
            val = 'nodeagent'          #
            if not quiet :
                print '%s() warning: "nodeagent" being used for ${SERVER}.' % funName
          else :                       #
            break                      #
        elif name == 'CELL' :          #
          if variables.has_key( 'WAS_CELL_NAME' ) :
            val = variables[ 'WAS_CELL_NAME' ]
            if not quiet :
              print '%s() warning: "${WAS_CELL_NAME}" being used instead of ${CELL}.' % funName
          else :                       #
            break                      #
        else :                         #
          print '%s() error - Unknown variable: "%s"' % ( funName, name ) 
          print '\t"%s"' % value
          break                        # We're done
      else :                           # The specified variable has a value
        val = variables[ name ]        #   ... use it
        if val == '[]' :               # Check for an "empty string"
          val = ''                     #
#     value = re.sub( var, val, value, 1 ) 
      value = value.replace( '${%s}' % name, val, 1 ) 
    else :
      print '%s() error - No substitution found.' % funName 
      break                            # be sure to terminate the loop
  return value 


#-------------------------------------------------------------------------------
# Name: Usage()
# Role: Display information about how the library module should be used.
#-------------------------------------------------------------------------------
def Usage( cmd = 'WAuJ_utilities' ) :
  'Usage( cmd ) - Display the usage information for the module.'
  #-----------------------------------------------------------------------------
  # To be able to access to the module docstring (i.e., __doc__), we
  # have to:
  #-----------------------------------------------------------------------------
  # 1. Define a global variable, and bind the value of __doc__ to it
  #    (see below)
  # 2. Copy the contents of the global variable to a local variable
  #    This lets us use locals() to access the value.
  #-----------------------------------------------------------------------------
  info = docstring

  print '''     File: %(cmd)s.py
%(info)s
 Examples:
   import %(cmd)s as WAuJ\n
   ...
   if WAuJ.localMode() :
     print "Connection required."''' % locals()


#-------------------------------------------------------------------------------
# Name: WSASvariables()
# Role: Return a dictionary of the specific WebSphere Application
#       Server (WSAS) variables for the specified resource (i.e.,
#       Server, Node, ServerCluster, ClusterMember, or Cell).
# History:
#   when    who ver  what
# --------  --- ---- ----------
# 11/09/22  rag 0.5  Fix Change main code to use only getType()
# 11/05/10  rag 0.4  Fix Typo for resolving cluster used Node instead of
#                        ServerCluster, and it tried using itemDict[ 'cells' ]
#                        instead of cfgDict[ 'cells' ]
# 11/05/02  rag 0.3  Fix AdminConfig.getObjectType() doesn't exist in ver 6.1
# 10/05/19  rag 0.2  Fix Use AdminConfig.getObjectType()
# 10/04/22  rag 0.1  Add docstring
# 10/04/18  rag 0.0  New
#-------------------------------------------------------------------------------
def WSASvariables( configId ) :
  'WSASvariables( configId ) - Return a dictionary of the WSAS variables.'

  #-----------------------------------------------------------------------------
  # Name: getType()
  # Role: Used to simulate AdminConfig.getObjectType() for a WSAS 6.1
  #       environment
  #-----------------------------------------------------------------------------
  def getType( configId ) :
    Type = 'unknownType'
    try :
      Type = AdminConfig.getObjectType( configId )
    except :
      for Type in 'Server,ClusterMember,Node,ServerCluster,Cell'.split( ',' ) :
        for s in AdminConfig.list( Type ).splitlines() :
          if s == configId :
            return Type
    return Type

  result = {}
  mo = re.compile( '\.xml#(\w+)_\d+\)$' ).search( configId )
# print callerName(), 'mo:', mo
  if mo :
    cfgDict  = configIdAsDict( configId )
    itemDict = showAsDict( configId )

    #---------------------------------------------------------------------------
    # Extract the configuration type from the configId
    #---------------------------------------------------------------------------
    Type = getType( configId )
#   print 'Type:', Type

    if Type == 'Server' :
      #-------------------------------------------------------------------------
      # We were provided with the server configId
      #-------------------------------------------------------------------------
      serverVM   = scopedWSASvariables( configId )

      #-------------------------------------------------------------------------
      # Build the configId of the containing Node
      #-------------------------------------------------------------------------
      nodePrefix = '(cells/%(cells)s/nodes/%(nodes)s|' % cfgDict
      nodeId     = configIdFilter( 'Node', nodePrefix )
      nodeVM     = scopedWSASvariables( nodeId )

      #-------------------------------------------------------------------------
      # Build the configId of the containing Cell
      #-------------------------------------------------------------------------
      cellPrefix = '(cells/%(cells)s|' % cfgDict
      cellId     = configIdFilter( 'Cell', cellPrefix )

      #-------------------------------------------------------------------------
      # Start with the cell level variables.
      #-------------------------------------------------------------------------
      result     = scopedWSASvariables( cellId )

      #-------------------------------------------------------------------------
      # If the server is a member of a cluster, get that configId too.
      # And add any of these to the result.
      #-------------------------------------------------------------------------
      if itemDict.has_key( 'clusterName' ) :
        clusterPrefix = '(cells/%s/clusters/%s|' % ( cfgDict[ 'cells' ], itemDict[ 'clusterName' ] )
        clusterId     = configIdFilter( 'ServerCluster', clusterPrefix )
        result.update( scopedWSASvariables( clusterId ) )

      #-------------------------------------------------------------------------
      # Finally, add the Node and server variables to the dictionary.
      #-------------------------------------------------------------------------
      result.update( nodeVM )
      result.update( serverVM )
      return result

    #---------------------------------------------------------------------------
    # For a ClusterMember, the result = Cell level variable + any
    # cluster level variables + any that the cluster member may have.
    #---------------------------------------------------------------------------
    if Type == 'ClusterMember' :
      cellPrefix = '(cells/%(cells)s|' % cfgDict
      cellId     = configIdFilter( 'Cell', cellPrefix )
      result     = scopedWSASvariables( cellId )
      result.update( scopedWSASvariables( itemDict[ 'cluster' ] ) )
      result.update( scopedWSASvariables( configId ) )
      return result

    #---------------------------------------------------------------------------
    # For a Nodes & Clusters, the result = Cell level variable + any
    # variables for the specified resource.
    #---------------------------------------------------------------------------
    if ( Type == 'Node' ) or ( Type == 'ServerCluster' ) :
      cellPrefix = '(cells/%(cells)s|' % cfgDict
      cellId     = configIdFilter( 'Cell', cellPrefix )
      result     = scopedWSASvariables( cellId )
      result.update( scopedWSASvariables( configId ) )
      return result

    #---------------------------------------------------------------------------
    # The Cell is easy... just the cell level variables.
    #---------------------------------------------------------------------------
    if Type == 'Cell' :
      result     = scopedWSASvariables( configId )
      return result

    else :
      print '%s(): error - unrecognized configId type: "%s"' % ( callerName(), Type )
  else :
    print '%s(): error - unrecognized configId string: %s' % ( callerName(), configId )

  return


#-------------------------------------------------------------------------------
# main: Verify that this file was imported, and not executed.
# Note: Version 6.x works differently.
#       We need to check for, and import the WSAS scripting objects 
#-------------------------------------------------------------------------------
docstring = __doc__
if ( __name__ == 'main' ) or ( __name__ == '__main__' ) :
  Usage( __name__ )
else :
  if 'Help' not in dir() :
    try :
      import Help
    except :
      pass
  if 'AdminApp' not in dir() :
    try :
      import AdminApp
    except :
      pass
  if 'AdminConfig' not in dir() :
    try :
      import AdminConfig
    except :
      pass
  if 'AdminControl' not in dir() :
    try :
      import AdminControl
    except :
      pass
  if 'AdminTask' not in dir() :
    try :
      import AdminTask
    except :
      pass

