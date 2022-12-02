#!/usr/bin/env python3
# Copyright (c) 2015-2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://www.opensource.org/licenses/mit-license.php.
"""Test node responses to invalid transactions.

In this test we connect to one node over p2p, and test tx requests.
"""

from test_framework.blocktools import create_block, create_coinbase, create_transaction
from test_framework.messages import (
    COIN,
    COutPoint,
    CTransaction,
    CTxIn,
    CTxOut,
)
from test_framework.mininode import P2PDataStore
from test_framework.script import (
    CScript,
    OP_NOTIF,
    OP_TRUE,
    OP_DROP
)
from test_framework.test_framework import FreedomCoinTestFramework
from test_framework.util import (
    assert_equal,
)


class InvalidTxRequestTest(FreedomCoinTestFramework):
    def set_test_params(self):
        self.num_nodes = 1
        self.setup_clean_chain = True
        self.extra_args = [["-acceptnonstdtxn=1"]]

    def bootstrap_p2p(self, *, num_connections=1):
        """Add a P2P connection to the node.

        Helper to connect and wait for version handshake."""
        for _ in range(num_connections):
            self.nodes[0].add_p2p_connection(P2PDataStore())
        self.nodes[0].p2p.wait_for_verack()

    def reconnect_p2p(self, **kwargs):
        """Tear down and bootstrap the P2P connection to the node.

        The node gets disconnected several times in this test. This helper
        method reconnects the p2p and restarts the network thread."""
        self.nodes[0].disconnect_p2ps()
        self.bootstrap_p2p(**kwargs)

    def new_spend_tx(self, prev_hash, prev_n, tx_outs):
        """Create a CTransaction spending COutPoint(prev_hash, prev_n) to the CTxOut-list tx_outs."""
        tx = CTransaction()
        tx.vin.append(CTxIn(outpoint=COutPoint(prev_hash, prev_n)))
        tx.vout = tx_outs
        tx.calc_sha256()
        return tx

    def run_test(self):
        node = self.nodes[0]  # convenience reference to the node

        self.bootstrap_p2p()  # Add one p2p connection to the node

        best_block = self.nodes[0].getbestblockhash()
        tip = int(best_block, 16)
        best_block_time = self.nodes[0].getblock(best_block)['time']
        block_time = best_block_time + 1

        self.log.info("Create a new block with an anyone-can-spend coinbase.")
        height = 1
        block = create_block(tip, create_coinbase(height), block_time)
        block.solve()
        # Save the coinbase for later
        block1 = block
        tip = block.sha256
        node.p2p.send_blocks_and_test([block], node, success=True)

        self.log.info("Mature the block.")
        self.nodes[0].generate(100)

        # Transaction will be rejected with code 16 (REJECT_INVALID)
        # and we get disconnected immediately
        self.log.info('Test a transaction that is rejected')
        tx1 = create_transaction(block1.vtx[0], 0, CScript([OP_NOTIF]), 50 * COIN - 12000)
        node.p2p.send_txs_and_test([tx1], node, success=False, expect_disconnect=True)

        # Make two p2p connections to provide the node with orphans
        # * p2ps[0] will send valid orphan txs (one with low fee)
        # * p2ps[1] will send an invalid orphan tx (and is later disconnected for that)
        self.reconnect_p2p(num_connections=2)

        self.log.info('Test orphan transaction handling ... ')
        SCRIPT_PUB_KEY_OP_TRUE = CScript([OP_TRUE, OP_DROP] * 15 + [OP_TRUE])
        # Create a root transaction that we withhold until all dependend transactions
        # are sent out and in the orphan cache
        tx_withhold = self.new_spend_tx(block1.vtx[0].sha256, 0, [CTxOut(nValue=50 * COIN - 12000, scriptPubKey=SCRIPT_PUB_KEY_OP_TRUE)])

        # Our first orphan tx with 3 outputs to create further orphan txs
        tx_orphan_1 = self.new_spend_tx(tx_withhold.sha256, 0, [CTxOut(nValue=10 * COIN, scriptPubKey=SCRIPT_PUB_KEY_OP_TRUE)] * 3)

        # A valid transaction with low fee
        tx_orphan_2_no_fee = self.new_spend_tx(tx_orphan_1.sha256, 0, [CTxOut(nValue=10 * COIN, scriptPubKey=SCRIPT_PUB_KEY_OP_TRUE)])

        # A valid transaction with sufficient fee
        tx_orphan_2_valid = self.new_spend_tx(tx_orphan_1.sha256, 1, [CTxOut(nValue=10 * COIN - 12000, scriptPubKey=SCRIPT_PUB_KEY_OP_TRUE)])

        # An invalid transaction with negative fee
        tx_orphan_2_invalid = self.new_spend_tx(tx_orphan_1.sha256, 2, [CTxOut(nValue=11 * COIN, scriptPubKey=SCRIPT_PUB_KEY_OP_TRUE)])

        self.log.info('Send the orphans ... ')
        # Send valid orphan txs from p2ps[0]
        node.p2p.send_txs_and_test([tx_orphan_1, tx_orphan_2_no_fee, tx_orphan_2_valid], node, success=False)
        # Send invalid tx from p2ps[1]
        node.p2ps[1].send_txs_and_test([tx_orphan_2_invalid], node, success=False)

        assert_equal(0, node.getmempoolinfo()['size'])  # Mempool should be empty
        assert_equal(2, len(node.getpeerinfo()))  # p2ps[1] is still connected

        self.log.info('Send the withhold tx ... ')
        node.p2p.send_txs_and_test([tx_withhold], node, success=True)

        # Transactions that should end up in the mempool
        expected_mempool = {
            t.hash
            for t in [
                tx_withhold,  # The transaction that is the root for all orphans
                tx_orphan_1,  # The orphan transaction that splits the coins
                tx_orphan_2_valid,  # The valid transaction (with sufficient fee)
            ]
        }
        # Transactions that do not end up in the mempool
        # tx_orphan_no_fee, because it has too low fee (p2ps[0] is not disconnected for relaying that tx)
        # tx_orphan_invalid, because it has negative fee (p2ps[1] is disconnected for relaying that tx)

        # future to do: p2ps[1] is still connected because we aren't banning the peer, we are just removing
        # 'tx_orphan_2_invalid' transaction from the orphans pool.
        #wait_until(lambda: 1 == len(node.getpeerinfo()), timeout=12)  # p2ps[1] is no longer connected
        assert_equal(expected_mempool, set(node.getrawmempool()))

        self.log.info('Test orphan pool overflow')
        orphan_tx_pool = [CTransaction() for _ in range(101)]
        for i in range(len(orphan_tx_pool)):
            orphan_tx_pool[i].vin.append(CTxIn(outpoint=COutPoint(i, 333)))
            orphan_tx_pool[i].vout.append(CTxOut(nValue=11 * COIN, scriptPubKey=SCRIPT_PUB_KEY_OP_TRUE))

        with node.assert_debug_log(['mapOrphan overflow, removed 1 tx']):
            node.p2p.send_txs_and_test(orphan_tx_pool, node, success=False)

        rejected_parent = CTransaction()
        rejected_parent.vin.append(CTxIn(outpoint=COutPoint(tx_orphan_2_invalid.sha256, 0)))
        rejected_parent.vout.append(CTxOut(nValue=11 * COIN, scriptPubKey=SCRIPT_PUB_KEY_OP_TRUE))
        rejected_parent.rehash()
        with node.assert_debug_log(['not keeping orphan with rejected parents {}'.format(rejected_parent.hash)]):
            node.p2p.send_txs_and_test([rejected_parent], node, success=False)


if __name__ == '__main__':
    InvalidTxRequestTest().main()
