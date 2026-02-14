function calculateCost() {
  const fabricType = document.getElementById('fabric-type').value;
  const fabricPerMeterRate = parseFloat(document.getElementById('fabric-per-meter-rate').value);
  const countOfYarn = parseFloat(document.getElementById('count-of-yarn').value);
  const widthOfFabric = parseFloat(document.getElementById('width-of-fabric').value);
  const quantity = parseFloat(document.getElementById('quantity').value);

  let yarnCostPerKg = 0;
  switch (fabricType) {
    case 'cotton':
      yarnCostPerKg = 2.50;
      break;
    case 'polyester':
      yarnCostPerKg = 3.00;
      break;
    default:
      yarnCostPerKg = 0;
  }

  const totalCost = (fabricPerMeterRate * quantity) + (countOfYarn * yarnCostPerKg * 0.5);
  document.getElementById('result').innerHTML = `The total cost of fabric is $${totalCost.toFixed(2)}`;
}