// Copyright (c) 2020 The FreedomCoin developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or https://www.opensource.org/licenses/mit-license.php.

#ifndef FreedomCoin_SAPLING_TEST_FIXTURE_H
#define FreedomCoin_SAPLING_TEST_FIXTURE_H

#include "test/test_freedomcoin.h"

/**
 * Testing setup that configures a complete environment for Sapling testing.
 */
struct SaplingTestingSetup : public TestingSetup
{
    SaplingTestingSetup(const std::string& chainName = CBaseChainParams::MAIN);
    ~SaplingTestingSetup();
};

/**
 * Regtest setup with sapling always active
 */
struct SaplingRegTestingSetup : public SaplingTestingSetup
{
    SaplingRegTestingSetup();
};


#endif //FreedomCoin_SAPLING_TEST_FIXTURE_H
