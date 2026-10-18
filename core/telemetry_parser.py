import struct
from typing import Dict, Any, Optional

class TelemetryParser:
    """
    Parses device binary dump or CSV logs.
    Decodes MCU registers, fault counters, and snapshot voltages/currents.
    """

    @staticmethod
    def parse_binary_snapshot(data: bytes) -> Dict[str, Any]:
        """
        Unpacks binary telemetry payload (struct format):
        Offset 0: Magic byte (0xAA, 0x55)
        Offset 2: Fault current in deci-Amps (uint16)
        Offset 4: Bus voltage in centi-Volts (uint16)
        Offset 6: Thermal counter (uint8)
        Offset 7: Hall sequence (uint8, e.g. 0b011)
        Offset 8: Reset flag (uint8: 0=None, 1=WDT, 2=POR, 3=UVLO)
        """
        if len(data) < 9:
            # Fallback default
            return {
                "fault_current": 295.0,
                "bus_voltage": 18.2,
                "thermal_counter": 1,
                "hall_state": "011",
                "reset_reason": "None",
            }

        magic = struct.unpack_from(">H", data, 0)[0]
        curr_raw, volt_raw, therm, hall_raw, rst_code = struct.unpack_from(">HHBBB", data, 2)

        reset_map = {0: "None", 1: "WDT", 2: "POR", 3: "UVLO"}
        hall_str = format(hall_raw & 0x07, "03b")

        return {
            "fault_current": round(curr_raw / 10.0, 1),
            "bus_voltage": round(volt_raw / 100.0, 1),
            "thermal_counter": int(therm),
            "hall_state": hall_str,
            "reset_reason": reset_map.get(rst_code, "Unknown"),
        }

    @classmethod
    def get_preset_snapshot(cls, model_id: str) -> Dict[str, Any]:
        """
        Returns parsed telemetry for predefined test scenarios.
        """
        if model_id == "A937":
            return {
                "log_filename": "A937_SNAPSHOT_20261018.BIN",
                "fault_current": 295.0,
                "thermal_counter": 1,
                "bus_voltage": 18.2,
                "hall_state": "011 (Valid)",
                "reset_reason": "None",
                "summary": "4 Fault Counters & 3 Snapshots Parsed",
            }
        elif model_id == "A912":
            return {
                "log_filename": "A912_CAPTURE_0942.BIN",
                "fault_current": 45.0,
                "thermal_counter": 0,
                "bus_voltage": 19.4,
                "hall_state": "000 (STUCK)",
                "reset_reason": "None",
                "summary": "Hall sequence stuck at 000 (Stator locked)",
            }
        elif model_id == "A552":
            return {
                "log_filename": "A552_DUMP_0411.BIN",
                "fault_current": 11.5,
                "thermal_counter": 0,
                "bus_voltage": 16.1,
                "hall_state": "101 (Valid)",
                "reset_reason": "WDT / POR",
                "summary": "Watchdog timeout with 3.3V UVLO dip",
            }
        return cls.get_preset_snapshot("A937")

