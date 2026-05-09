import { createClient } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const CONTRACT = '0x51dc509C851f2B96981f88C4C353fE488f172D4f';
const client = createClient({ chain: testnetBradbury });

console.log('Reading contract state...');

const total = await client.readContract({
  address: CONTRACT,
  functionName: 'get_total_claims',
  args: [],
});
console.log('Total claims:', total);

if (Number(total) > 0) {
  const claim = await client.readContract({
    address: CONTRACT,
    functionName: 'get_claim',
    args: [0],
  });
  console.log('Claim 0:', claim);
}
