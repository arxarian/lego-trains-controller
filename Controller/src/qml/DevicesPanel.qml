import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import TrainView

Item {
    id: root

    property int selectedRailIndex: -1
    property var selectedRail: null

    function refreshSelectedRail() {
        if (selectedRailIndex < 0 || selectedRailIndex >= rails.count) {
            selectedRail = null
            return
        }
        var rail = rails.get(selectedRailIndex)
        selectedRail = (rail && rail.is_switch()) ? rail : null
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth

        ColumnLayout {
            width: root.width - 20
            spacing: 12

            GroupBox {
                title: "Discovery"
                Layout.fillWidth: true

                RowLayout {
                    width: parent.width
                    Button {
                        text: "Discover"
                        onClicked: hubConnector.discover()
                    }
                    Button {
                        text: "Connect to Switch"
                        onClicked: hubConnector.connect_to("City Hub 2")
                    }
                    Button {
                        text: "Connect to Express Train"
                        onClicked: hubConnector.connect_to("City Hub 1")
                    }
                    Item { Layout.fillWidth: true }
                }
            }

            GroupBox {
                title: "Train hubs"
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(120, trainHubs.count * 56 + 40)

                ListView {
                    id: trainHubs
                    anchors.fill: parent
                    clip: true
                    model: trainDevices
                    delegate: RowLayout {
                        width: trainHubs.width
                        height: 48
                        spacing: 8

                        required property var object
                        required property int index

                        Text {
                            text: object.name + (object.initialized ? "" : " (waiting…)")
                            Layout.fillWidth: true
                        }
                        Button {
                            text: "Disconnect"
                            onClicked: object.disconnect()
                        }
                        Button {
                            text: "Shut down"
                            onClicked: object.shutDown()
                        }
                    }
                }
            }

            GroupBox {
                title: "Switch hubs"
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(140, switchHubs.count * 56 + 80)

                ColumnLayout {
                    anchors.fill: parent

                    Button {
                        text: "Add simulated switch"
                        onClicked: switchDevices.addSimulated()
                    }

                    ListView {
                        id: switchHubs
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: switchDevices
                        delegate: RowLayout {
                            width: switchHubs.width
                            height: 48
                            spacing: 8

                            required property var object
                            required property int index

                            Text {
                                text: object.name
                                      + (object.isSimulated ? " [sim]" : " [hw]")
                                      + " — " + object.boundRailLabel
                                      + " — pos " + object.position
                                Layout.fillWidth: true
                            }
                            Button {
                                text: "A"
                                highlighted: object.position === "A"
                                onClicked: object.setPosition("A")
                            }
                            Button {
                                text: "B"
                                highlighted: object.position === "B"
                                onClicked: object.setPosition("B")
                            }
                            Button {
                                text: "Disconnect"
                                onClicked: object.disconnect()
                            }
                            Button {
                                text: "Shut down"
                                onClicked: object.shutDown()
                            }
                        }
                    }
                }
            }

            GroupBox {
                title: "Switch rails"
                Layout.fillWidth: true
                Layout.preferredHeight: 220

                ColumnLayout {
                    anchors.fill: parent

                    ListView {
                        id: switchRails
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: rails
                        delegate: Rectangle {
                            id: railRow
                            required property var object
                            required property int index

                            property string boundDeviceName: object
                                ? switchDevices.deviceNameForRail(object) : ""

                            width: switchRails.width
                            height: object && object.is_switch() ? 40 : 0
                            visible: height > 0
                            color: root.selectedRailIndex === index ? "#cce5ff" : "transparent"

                            function refreshBoundDeviceName() {
                                boundDeviceName = object
                                    ? switchDevices.deviceNameForRail(object) : ""
                            }

                            Component.onCompleted: refreshBoundDeviceName()

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 4
                                spacing: 8
                                visible: railRow.visible

                                Text {
                                    text: "Rail " + object.id
                                          + " (" + (object.type === 2 ? "SwitchLeft" : "SwitchRight") + ")"
                                          + "  pos " + object.switch_position
                                          + "  —  " + railRow.boundDeviceName
                                    Layout.fillWidth: true
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                enabled: railRow.visible
                                onClicked: {
                                    root.selectedRailIndex = index
                                    root.selectedRail = object
                                }
                            }

                            Connections {
                                target: switchDevices
                                function onBindings_changed() {
                                    railRow.refreshBoundDeviceName()
                                }
                            }
                        }
                    }

                    RowLayout {
                        Button {
                            text: "Assign"
                            enabled: root.selectedRail !== null
                                     && switchDevices.deviceForRail(root.selectedRail) === null
                                     && switchDevices.unboundDevices().length > 0
                            onClicked: assignDialog.open()
                        }
                        Button {
                            text: "Unbind"
                            enabled: root.selectedRail !== null
                                     && switchDevices.deviceForRail(root.selectedRail) !== null
                            onClicked: switchDevices.unbindRail(root.selectedRail)
                        }
                        Item { Layout.fillWidth: true }
                    }
                }
            }
        }
    }

    Dialog {
        id: assignDialog
        title: "Assign switch hub"
        modal: true
        anchors.centerIn: Overlay.overlay
        standardButtons: Dialog.Cancel
        width: 320
        height: 280

        property var unbound: []
        property int chosen: -1

        onAboutToShow: {
            unbound = switchDevices.unboundDevices()
            chosen = unbound.length > 0 ? 0 : -1
        }

        ColumnLayout {
            anchors.fill: parent
            Label { text: "Unbound hubs:" }
            ListView {
                id: hubList
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: assignDialog.unbound
                currentIndex: assignDialog.chosen
                delegate: Rectangle {
                    required property int index
                    required property var modelData
                    width: hubList.width
                    height: 36
                    color: hubList.currentIndex === index ? "#cce5ff" : "transparent"
                    Text {
                        anchors.fill: parent
                        anchors.margins: 6
                        text: modelData.name
                        verticalAlignment: Text.AlignVCenter
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            hubList.currentIndex = index
                            assignDialog.chosen = index
                        }
                    }
                }
            }
            Button {
                text: "Assign"
                enabled: assignDialog.chosen >= 0 && root.selectedRail !== null
                onClicked: {
                    var device = assignDialog.unbound[assignDialog.chosen]
                    switchDevices.assignToRail(root.selectedRail, device)
                    assignDialog.close()
                }
            }
        }
    }
}
