# Nokia NRS Certification Lab

**Real OSPF/ISIS Protocol Lab Using FRRouting & Docker**

I built this hands-on lab to demonstrate actual routing protocol behavior for Nokia NRS certification preparation. It uses production-grade FRRouting in Docker containers - no simulations, real packets.

---

## Quick Start (Windows PowerShell)

```powershell
# Clone and run
cd real_networking
.\Nokia_NRS_Demo.ps1
```

Wait about 45 seconds for OSPF to converge, then check:

```powershell
docker exec R1 vtysh -c "show ip ospf neighbor"
```

---

## What I Built & Demonstrated

### 1. Real OSPF Protocol in Action
- **Watched OSPF adjacency form**: DOWN → INIT → 2-WAY → EXSTART → EXCHANGE → LOADING → FULL
- **Saw DR/BDR election happen**: Based on priority, Router ID as tie-breaker
- **Verified LSA exchange**: Type 1 Router LSAs and Type 2 Network LSAs in database
- **Real convergence timing**: Measured 40+ seconds for Dead Interval + SPF calculation

### 2. Production Troubleshooting Scenario
I intentionally created an MTU mismatch to demonstrate a common production failure:

**Before fix:**
```
R2 (2.2.2.2): FULL/Backup    ← Working
R3 (3.3.3.3): EXCHANGE/DR    ← Stuck! MTU mismatch
```

**Root cause:** R3 had MTU 1400, OSPF expects 1500 for DBD packets in EXCHANGE state.

**Applied fix:**
```bash
interface eth0
  ip ospf mtu-ignore
```

**After fix (40 seconds later):**
```
R2 (2.2.2.2): FULL/Backup    ← Still working
R3 (3.3.3.3): FULL/DR        ← Now fixed!
```

### 3. Hands-on Linux Networking
- **Docker networking**: Created containers, attached networks, configured IPs
- **FRRouting configuration**: Set up zebra/ospfd daemons, configured OSPF areas
- **Kernel routing tables**: Used `ip route show` to verify OSPF-learned routes
- **Interface management**: Set MTU with `ip link set eth0 mtu 1400`

---

## Why This Matters for Nokia

This isn't just theory - it's the same OSPF protocol Nokia SR-OS runs (RFC 2328). The troubleshooting methodology transfers directly:

| What I did in FRR | Equivalent in Nokia SR-OS |
|-------------------|---------------------------|
| `show ip ospf neighbor` | `show router ospf neighbor` |
| `show ip ospf database` | `show router ospf database` |
| `ip ospf mtu-ignore` | `configure router ospf interface mtu-ignore` |
| Checked interface MTU | `show port <port-id> detail` |

**Key insight:** MTU mismatches cause silent failures - adjacency looks like it's forming but gets stuck in EXCHANGE state. This happens with LAG interfaces, tunnels, and multi-vendor networks.

---

## My Learning Process

1. **Started simple**: Two routers, basic OSPF configuration
2. **Added complexity**: Third router with MTU mismatch to create failure scenario
3. **Troubleshot**: Checked neighbor states, verified MTU, understood why EXCHANGE state failed
4. **Fixed & verified**: Applied `mtu-ignore`, waited for convergence, confirmed database sync

The Docker networking had some challenges (IP conflicts, Windows path issues) which gave me real troubleshooting experience with container networking.

---

## Files I Created

```
real_networking/
├── Nokia_NRS_Demo.ps1       # Main setup - creates 3 routers with OSPF
├── demo_mtu_fix.ps1         # Shows MTU mismatch troubleshooting
├── nokia_ospf_working.ps1   # Alternative setup script
└── cleanup_lab.ps1          # Cleanup script

docs/sros_config_examples/   # Nokia SR-OS configuration examples
```

---

## Skills  

- **Real protocol understanding** - Not just commands, but why OSPF behaves certain ways
- **Production troubleshooting** - Diagnosed silent MTU failure, applied correct fix
- **Linux networking** - Docker, iproute2, kernel routing, FRR configuration
- **Methodical approach** - Verify → diagnose → fix → verify cycle
- **Convergence awareness** - Real timing, not simulated seconds

---

**Built for Nokia NRS-1/NRS-2 certification. Demonstrates real networking skills, not theory.**
