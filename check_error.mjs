import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const TX = "0xf9ad8d050da2a78bb5c3d501e5ad0125c54566c83105d02e43e91ca66b332775";
const client = createClient({ chain: testnetBradbury, account: createAccount(process.env.GL_KEY) });

const receipt = await client.waitForTransactionReceipt({ hash: TX, timeout: 30000 });

for (const [k, v] of Object.entries(receipt)) {
  if (['result', 'txExecutionResult', 'txExecutionResultName', 'resultName', 'eqBlocksOutputs'].includes(k)) {
    try { console.log(k, ':', JSON.stringify(v, (_, val) => typeof val === 'bigint' ? val.toString() : val, 2)); } 
    catch(e) { console.log(k, ':', String(v)); }
  }
}
