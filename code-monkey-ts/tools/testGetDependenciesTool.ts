import { GetDependenciesTool } from './getDependenciesTool';

async function testGetDependenciesTool() {
  const tool = new GetDependenciesTool();
  const input = {
    input: JSON.stringify({ module_names: ['module1', 'module2'] })
  };

  try {
    const result = await tool._call(input);
    console.log('Result:', result);
  } catch (error) {
    console.error('Error:', error);
  }
}

testGetDependenciesTool();
