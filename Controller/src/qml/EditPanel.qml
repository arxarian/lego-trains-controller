import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root

    readonly property real buttonWidth: 55

    spacing: 0

    Row {
        Button {
            text: "Save"
            onClicked: projectStorage.saveProject(project)
        }

        Button {
            text: "Load"
            onClicked: projectStorage.loadProject(project.name)
        }

        Button {
            text: "Generate big graph"
            onClicked: {
                projectStorage.loadProject("rails_big")
                network.generate()
            }
        }

        Button {
            text: "Generate small graph"
            onClicked: {
                projectStorage.loadProject("rails")
                network.generate()
            }
        }
    }

    ButtonGroup { id: group }

    GridLayout {
        columns: 6

        Label {
            text: "Rails"
        }

        Repeater {
            model: railTypes

            Button {
                id: railItem

                property RailType rail: model.object

                checked: Globals.selectedRail === index
                checkable: true
                text: railItem.rail.name

                onClicked: {
                    Globals.selectedMarker = -1
                    Globals.selectedRail = index
                    markerTypes.markersActive = false
                    railTypes.railsActive = true
                }

                ButtonGroup.group: group
                Layout.preferredWidth: root.buttonWidth
            }
        }

        Item {}

        Label {
            text: "Markers"
        }

        Repeater {
            model: markerTypes

            Button {
                id: markerItem

                property MarkerType marker: model.object

                checkable: true
                text: markerItem.marker.name

                onClicked: {
                    Globals.selectedMarker = index
                    Globals.selectedRail = -1
                    markerTypes.markersActive = true
                    railTypes.railsActive = false
                }

                ButtonGroup.group: group
                Layout.preferredWidth: root.buttonWidth
            }
        }
    }
}
