"""Regression tests for UNG system physics. Run: python -m unittest discover -s physics-engine -p 'test_*.py'"""
import unittest
from ung_system_physics import Link, Satellite, Vehicle, Shelf, check_link, check_orbit, check_vehicle, check_shelf

class SystemPhysicsTests(unittest.TestCase):
    def test_esp32_link(self):
        checks=check_link(Link("esp32",18,-90,2.4e9,30,("brick","brick")))
        self.assertEqual(checks[0].status,"OK")
    def test_warehouse_link(self):
        checks=check_link(Link("warehouse",20,-80,5.8e9,60,("concrete",),4))
        self.assertEqual(checks[0].status,"WARN")
    def test_satellite(self):
        checks=check_orbit(Satellite("weather",850,102))
        self.assertEqual(checks[-1].status,"OK")
    def test_overloaded_truck(self):
        checks=check_vehicle(Vehicle("truck",3000,3000,3500,80,"wet",60,120))
        self.assertEqual(checks[0].status,"FAIL")
        self.assertEqual(checks[1].status,"FAIL")
    def test_shelf_floor(self):
        checks=check_shelf(Shelf("rack A",800,700,1500,0.4,2,0.8))
        self.assertEqual(checks[1].status,"FAIL")
    def test_invalid_radio(self):
        with self.assertRaises(ValueError):
            check_link(Link("bad",18,-90,0,30))
    def test_zero_speed_trip(self):
        checks=check_vehicle(Vehicle("stopped",3000,3000,0,0,trip_km=10))
        self.assertEqual(checks[-1].status,"WARN")
if __name__=="__main__":
    unittest.main()
