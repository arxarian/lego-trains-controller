import QtQuick

Item {
    id: root

    readonly property bool selected: root.activeFocus
    property bool propagateComposedEvents: false

    function deleteAction() {
        console.warn("no delete action defined")
    }

    z: root.selected ? 10 : 0

    focus: true

    Keys.onPressed: (event)=> {
                        if (event.key === Qt.Key_Delete) {
                            root.deleteAction()
                            event.accepted = true
                        }
                    }

    SelectedMarker {
        anchors.fill: parent
        anchors.margins: -radius / 2
        z: 10
        visible: root.selected
    }

    MouseArea {
        anchors.fill: parent
        propagateComposedEvents: root.propagateComposedEvents
        onClicked: function(mouse) {
            mouse.accepted = !propagateComposedEvents
            root.forceActiveFocus()
        }
    }
}
