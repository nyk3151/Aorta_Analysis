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

#ifndef __qnykAorticAppMainWindow_h
#define __qnykAorticAppMainWindow_h

// nykAortic includes
#include "qnykAorticAppExport.h"
class qnykAorticAppMainWindowPrivate;

// Slicer includes
#include "qSlicerMainWindow.h"

class Q_NYKAORTIC_APP_EXPORT qnykAorticAppMainWindow : public qSlicerMainWindow
{
  Q_OBJECT
public:
  typedef qSlicerMainWindow Superclass;

  qnykAorticAppMainWindow(QWidget *parent=0);
  virtual ~qnykAorticAppMainWindow();

public slots:
  void on_HelpAboutnykAorticAppAction_triggered();

protected:
  qnykAorticAppMainWindow(qnykAorticAppMainWindowPrivate* pimpl, QWidget* parent);

private:
  Q_DECLARE_PRIVATE(qnykAorticAppMainWindow);
  Q_DISABLE_COPY(qnykAorticAppMainWindow);
};

#endif
