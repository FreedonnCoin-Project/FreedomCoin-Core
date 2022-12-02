// Copyright (c) 2018 The FreedomCoin developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef FreedomCoin_SPENDTYPE_H
#define FreedomCoin_SPENDTYPE_H

#include <cstdint>

namespace libzerocoin {
    enum SpendType : uint8_t {
        SPEND, // Used for a typical spend transaction, zFREED should be unusable after
        STAKE, // Used for a spend that occurs as a stake
        PN_COLLATERAL, // Used when proving ownership of zFREED that will be used for patriotnodes (future)
        SIGN_MESSAGE // Used to sign messages that do not belong above (future)
    };
}

#endif //FreedomCoin_SPENDTYPE_H
