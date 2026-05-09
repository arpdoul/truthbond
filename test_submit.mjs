import { createClient, createAccount } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';

const CONTRACT = '0x51dc509C851f2B96981f88C4C353fE488f172D4f';

// Read key from env variable instead of argument
const rawKey = process.env.GL_KEY || '';
const key = rawKey.startsWith('0x') ? rawKey : '0x' + rawKey;

if (!rawKey) {
  console.error('Set GL_KEY environment variable');
  process.exit(1);
}

console.log('Key length:', key.length);
console.log('Contract:', CONTRACT);

const account = createAccount(key);
const client = createClient({ chain: testnetBradbury, account });

console.log('Submitting claim...');
const hash = await client.writeContract({
  address: CONTRACT,
  functionName: 'submit_claim',
  args: ['https://www.theonion.com/nation-s-rich-increasingly-outsourcing-their-own-deaths-1850937933'],
  value: BigInt(0),
});

console.log('SUCCESS! TX:', hash);
console.log('Explorer:', 'https://explorer-bradbury.genlayer.com/tx/' + hash);
