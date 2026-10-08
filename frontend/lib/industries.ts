export type Machine = { id: string; name: string; kw: number; efficiency: number };
export type Industry = {
  id: string; name: string; icon: string; desc: string;
  rate: number; machines: Machine[];
};

export const INDUSTRIES: Industry[] = [
  { id: "pharmacy", name: "Pharmacy", icon: "💊",
    desc: "Clean rooms, HVAC and tablet production energy analysis.", rate: 8.5,
    machines: [
      { id: "hvac", name: "HVAC System", kw: 45, efficiency: 78 },
      { id: "compressor", name: "Air Compressor", kw: 37, efficiency: 72 },
      { id: "fbd", name: "Fluid Bed Dryer", kw: 22, efficiency: 81 },
      { id: "tablet", name: "Tablet Compression Machine", kw: 15, efficiency: 85 },
      { id: "chiller", name: "Chiller Plant", kw: 60, efficiency: 76 },
    ]},
  { id: "dairy", name: "Dairy", icon: "🥛",
    desc: "Chilling, pasteurizing and refrigeration load tracking.", rate: 8.0,
    machines: [
      { id: "chilling", name: "Milk Chilling Plant", kw: 40, efficiency: 80 },
      { id: "pasteurizer", name: "Pasteurizer", kw: 25, efficiency: 83 },
      { id: "homogenizer", name: "Homogenizer", kw: 30, efficiency: 79 },
      { id: "refcomp", name: "Refrigeration Compressor", kw: 55, efficiency: 74 },
      { id: "boiler", name: "Boiler", kw: 35, efficiency: 77 },
    ]},
  { id: "steel", name: "Steel", icon: "🏭",
    desc: "Furnace, rolling mill and heavy motor consumption.", rate: 7.2,
    machines: [
      { id: "eaf", name: "Electric Arc Furnace", kw: 500, efficiency: 70 },
      { id: "rolling", name: "Rolling Mill", kw: 250, efficiency: 75 },
      { id: "induction", name: "Induction Furnace", kw: 300, efficiency: 72 },
      { id: "compressor", name: "Air Compressor", kw: 75, efficiency: 73 },
      { id: "pump", name: "Cooling Water Pump", kw: 30, efficiency: 82 },
    ]},
  { id: "coldstorage", name: "Cold Storage", icon: "❄️",
    desc: "Compressor, evaporator and condenser energy insights.", rate: 8.2,
    machines: [
      { id: "refcomp", name: "Refrigeration Compressor", kw: 70, efficiency: 75 },
      { id: "evap", name: "Evaporator Fan", kw: 12, efficiency: 84 },
      { id: "condenser", name: "Condenser Unit", kw: 25, efficiency: 79 },
      { id: "towerpump", name: "Cooling Tower Pump", kw: 15, efficiency: 81 },
      { id: "hvac", name: "HVAC System", kw: 20, efficiency: 80 },
    ]},
];

export const getIndustry = (id: string) => INDUSTRIES.find(i => i.id === id);