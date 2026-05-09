import { createPublicClient, http } from 'viem';

const client = createPublicClient({
  transport: http("https://rpc.bradbury.genlayer.com"),
});

const receipt = await client.getTransactionReceipt({ 
  hash: "0xe31c05bc825e69474e3edda3398dbe3f1ba95ad3f081b86c5e71a4bf68a72bf9"
});

console.log(JSON.stringify(receipt, null, 2));
