import { createPublicClient, http } from 'viem';

const TX = "0x68ac0ef1de11e77b7db9f8ef8da4471702fc6dcd81bcfc57a98a4cd7a914e85c";

const client = createPublicClient({
  transport: http("https://rpc.bradbury.genlayer.com"),
});

const receipt = await client.getTransactionReceipt({ hash: TX });
console.log("Contract Address:", receipt.contractAddress);
