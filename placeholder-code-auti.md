@workspace Please audit the entire pylua_bioxen_vm_lib codebase and generate a comprehensive report identifying all placeholder implementations, incomplete features, and TODO items. Focus on:

1. **XCP-ng Integration Completeness**
   - Compare implemented XAPI methods against full XCP-ng API coverage
   - Identify missing VM lifecycle operations (clone, migrate, snapshot, suspend/resume)
   - Check for placeholder storage management (SR operations, VDI management)
   - Audit network management features (VLAN, bonding, QoS)
   - Verify high availability and clustering support

2. **Networking Feature Implementation**
   - Analyze NetworkedLuaVM class for actual vs placeholder functionality
   - Check LuaSocket integration completeness
   - Identify missing inter-VM communication features
   - Audit HTTP/REST API capabilities
   - Verify database connectivity features

3. **Code Quality Indicators**
   - Find functions with only `pass` statements or minimal implementations
   - Identify methods that return hardcoded mock data
   - Look for TODO, FIXME, PLACEHOLDER, or STUB comments
   - Check for exception handling that catches but doesn't properly handle
   - Find logging statements that indicate incomplete features

4. **Configuration and Error Handling**
   - Audit configuration validation completeness
   - Check error handling coverage for all operations
   - Identify missing retry logic and resilience patterns
   - Verify resource cleanup and connection management

Generate a structured report with specific file paths, line numbers, and severity levels (Critical/High/Medium/Low) for each finding.

@workspace Focus specifically on XCP-ng related files (xapi_client.py, xcp_ng_integration.py, ssh_session.py). Analyze:

- Which XAPI methods are actually implemented vs stubbed?
- Are VM operations (start/stop/clone/migrate) fully functional?
- Is storage management (create/resize/snapshot VDIs) implemented?
- Are network operations beyond basic connectivity supported?
- Is error handling comprehensive for XAPI failures?
- Are SSH operations robust with proper timeout and retry logic?

For each incomplete area, provide:
1. Current implementation status
2. What's missing for production readiness
3. Estimated complexity to complete
4. Dependencies on external XCP-ng infrastructure