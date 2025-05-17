/*==============================================================================

  Copyright (c) Kitware, Inc.

  See http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Julien Finet, Kitware, Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// nykAortic includes
#include "qnykAorticAppMainWindow.h"
#include "qnykAorticAppMainWindow_p.h"

// Qt includes
#include <QDesktopWidget>
#include <QHBoxLayout>
#include <QLabel>

// Slicer includes
#include "qSlicerApplication.h"
#include "qSlicerAboutDialog.h"
#include "qSlicerMainWindow_p.h"
#include "qSlicerModuleSelectorToolBar.h"

//-----------------------------------------------------------------------------
// qnykAorticAppMainWindowPrivate methods

qnykAorticAppMainWindowPrivate::qnykAorticAppMainWindowPrivate(qnykAorticAppMainWindow& object)
  : Superclass(object)
{
}

//-----------------------------------------------------------------------------
qnykAorticAppMainWindowPrivate::~qnykAorticAppMainWindowPrivate()
{
}

//-----------------------------------------------------------------------------
void qnykAorticAppMainWindowPrivate::init()
{
#if (QT_VERSION >= QT_VERSION_CHECK(5, 7, 0))
  QApplication::setAttribute(Qt::AA_UseHighDpiPixmaps);
#endif
  Q_Q(qnykAorticAppMainWindow);
  this->Superclass::init();
}

//-----------------------------------------------------------------------------
void qnykAorticAppMainWindowPrivate::setupUi(QMainWindow * mainWindow)
{
  qSlicerApplication * app = qSlicerApplication::application();

  //----------------------------------------------------------------------------
  // Add actions
  //----------------------------------------------------------------------------
  QAction* helpAboutSlicerAppAction = new QAction(mainWindow);
  helpAboutSlicerAppAction->setObjectName("HelpAboutnykAorticAppAction");
  helpAboutSlicerAppAction->setText("About " + app->applicationName());

  //----------------------------------------------------------------------------
  // Calling "setupUi()" after adding the actions above allows the call
  // to "QMetaObject::connectSlotsByName()" done in "setupUi()" to
  // successfully connect each slot with its corresponding action.
  this->Superclass::setupUi(mainWindow);

  // Add Help Menu Action
  this->HelpMenu->addAction(helpAboutSlicerAppAction);

  //----------------------------------------------------------------------------
  // Configure
  //----------------------------------------------------------------------------
  mainWindow->setWindowIcon(QIcon(":/Icons/Medium/DesktopIcon.png"));

  QLabel* logoLabel = new QLabel();
  logoLabel->setObjectName("LogoLabel");
  QPixmap logoPixmap(":/LogoFull.png");
  qDebug() << "Logo pixmap is" << (logoPixmap.isNull() ? "NULL" : "valid") << "with size" << logoPixmap.size();
  logoLabel->setPixmap(logoPixmap);
  logoLabel->setAlignment(Qt::AlignLeft | Qt::AlignVCenter);
  logoLabel->setContentsMargins(5, 0, 0, 0);
  logoLabel->setStyleSheet("QLabel#LogoLabel { background-color: transparent; padding: 2px; margin-right: 10px; }");
  logoLabel->setVisible(true);

  // Create a custom title bar widget that separates the logo from other content
  QWidget* customTitleBar = new QWidget();
  customTitleBar->setMinimumHeight(25); // Ensure title bar has minimum height
  QHBoxLayout* titleLayout = new QHBoxLayout(customTitleBar);
  titleLayout->setContentsMargins(0, 0, 0, 0);
  titleLayout->setSpacing(10);

  // Add the logo to the left side of the title bar
  titleLayout->addWidget(logoLabel);

  // Add spacer to push other content to the right
  titleLayout->addStretch(1);

  this->PanelDockWidget->setTitleBarWidget(customTitleBar);

  // Hide the menus
  //this->menubar->setVisible(false);
  //this->FileMenu->setVisible(false);
  //this->EditMenu->setVisible(false);
  //this->ViewMenu->setVisible(false);
  //this->LayoutMenu->setVisible(false);
  //this->HelpMenu->setVisible(false);
}

//-----------------------------------------------------------------------------
// qnykAorticAppMainWindow methods

//-----------------------------------------------------------------------------
qnykAorticAppMainWindow::qnykAorticAppMainWindow(QWidget* windowParent)
  : Superclass(new qnykAorticAppMainWindowPrivate(*this), windowParent)
{
  Q_D(qnykAorticAppMainWindow);
  d->init();
}

//-----------------------------------------------------------------------------
qnykAorticAppMainWindow::qnykAorticAppMainWindow(
  qnykAorticAppMainWindowPrivate* pimpl, QWidget* windowParent)
  : Superclass(pimpl, windowParent)
{
  // init() is called by derived class.
}

//-----------------------------------------------------------------------------
qnykAorticAppMainWindow::~qnykAorticAppMainWindow()
{
}

//-----------------------------------------------------------------------------
void qnykAorticAppMainWindow::on_HelpAboutnykAorticAppAction_triggered()
{
  qSlicerAboutDialog about(this);
  about.setLogo(QPixmap(":/Logo.png"));
  about.exec();
}
