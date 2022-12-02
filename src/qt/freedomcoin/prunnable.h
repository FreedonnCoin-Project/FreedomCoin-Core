// Copyright (c) 2019 The FreedomCoin developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef FreedomCoin_CORE_NEW_GUI_PRUNNABLE_H
#define FreedomCoin_CORE_NEW_GUI_PRUNNABLE_H

class Runnable {
public:
    virtual void run(int type) = 0;
    virtual void onError(QString error, int type) = 0;
};

#endif //FreedomCoin_CORE_NEW_GUI_PRUNNABLE_H
