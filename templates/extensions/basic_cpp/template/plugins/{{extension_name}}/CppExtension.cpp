/*
 * SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */

#define CARB_EXPORTS

#include <carb/PluginUtils.h>
#include <carb/logging/Log.h>

#include <omni/ext/IExt.h>
#include <omni/kit/IApp.h>

#include <memory>


#define EXTENSION_NAME "{{ extension_name }}.plugin"

using namespace carb;

// Plugin Implementation Descriptor
const struct carb::PluginImplDesc kPluginImpl = {
    EXTENSION_NAME,  // Name of the plugin (e.g. "carb.dictionary.plugin"). Must be globally unique.
    "Example of a native plugin extension.",  // Helpful text describing the plugin.  Used for debugging/tools.
    "NVIDIA",  // Author
    carb::PluginHotReload::eEnabled,  // If hot reloading is supported by the plugin.  (Note: hot reloading is deprecated)
    "dev"  // Build version of the plugin.
};

// List dependencies for this plugin
CARB_PLUGIN_IMPL_DEPS(omni::kit::IApp, carb::logging::ILogging)


class NativeExtensionExample : public omni::ext::IExt
{
public:
    void onStartup(const char* extId) override
    {
        printf(EXTENSION_NAME ": in onStartup\n");
        // Get app interface using Carbonite Framework
        omni::kit::IApp* app = carb::getFramework()->acquireInterface<omni::kit::IApp>();

        // Subscribe to update events and count them
        m_holder = carb::events::createSubscriptionToPop(
            app->getUpdateEventStream(),
            [this](carb::events::IEvent* event)
            {
                if (m_counter % 100 == 0)
                {
                    printf(EXTENSION_NAME ": %d updates passed.\n", m_counter);
                    CARB_LOG_INFO(EXTENSION_NAME ": %d updates passed.\n", m_counter);
                }
                m_counter++;
            });
    }

    void onShutdown() override
    {
        // Unsubscribes from the event stream
        m_holder = nullptr;
    }

private:
    int m_counter = 0;
    carb::ObjectPtr<carb::events::ISubscription> m_holder;
};

// Generate boilerplate code
CARB_PLUGIN_IMPL(kPluginImpl, NativeExtensionExample)

// There must be a fillInterface(InterfaceType&) function for each interface type that is exported by this plugin.
void fillInterface(NativeExtensionExample& iface)
{
}
