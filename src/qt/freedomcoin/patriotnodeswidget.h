// Copyright (c) 2019-2020 The FreedomCoin developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef PATRIOTNODESWIDGET_H
#define PATRIOTNODESWIDGET_H

#include "qt/freedomcoin/pwidget.h"
#include "qt/freedomcoin/furabstractlistitemdelegate.h"
#include "qt/freedomcoin/mnmodel.h"
#include "qt/freedomcoin/tooltipmenu.h"
#include "walletmodel.h"

#include <atomic>

#include <QTimer>
#include <QWidget>

class FreedomCoinGUI;

namespace Ui {
class PatriotNodesWidget;
}

QT_BEGIN_NAMESPACE
class QModelIndex;
QT_END_NAMESPACE

class PatriotNodesWidget : public PWidget
{
    Q_OBJECT

public:

    explicit PatriotNodesWidget(FreedomCoinGUI *parent = nullptr);
    ~PatriotNodesWidget();

    void loadWalletModel() override;

    void run(int type) override;
    void onError(QString error, int type) override;

    void showEvent(QShowEvent *event) override;
    void hideEvent(QHideEvent *event) override;

private Q_SLOTS:
    void onCreatePNClicked();
    void onStartAllClicked(int type);
    void changeTheme(bool isLightTheme, QString &theme) override;
    void onPNClicked(const QModelIndex &index);
    void onEditPNClicked();
    void onDeletePNClicked();
    void onInfoPNClicked();
    void updateListState();
    void updateModelAndInform(const QString& informText);

private:
    Ui::PatriotNodesWidget *ui;
    FurAbstractListItemDelegate *delegate;
    PNModel *mnModel = nullptr;
    TooltipMenu* menu = nullptr;
    QModelIndex index;
    QTimer *timer = nullptr;

    std::atomic<bool> isLoading;

    bool checkPNsNetwork();
    void startAlias(const QString& strAlias);
    bool startAll(QString& failedPN, bool onlyMissing);
    bool startPN(const CPatriotnodeConfig::CPatriotnodeEntry& mne, std::string& strError);
};

#endif // PATRIOTNODESWIDGET_H
