// Copyright (c) 2014 Arista Networks, Inc.  All rights reserved.
// Arista Networks, Inc. Confidential and Proprietary.

#include <eos/agent.h>
#include <eos/sdk.h>
#include <eos/tracing.h>

class SkeletonAgent : public eos::agent_handler {
 public:
   eos::tracer tracer;

   explicit SkeletonAgent(eos::sdk & sdk):
        eos::agent_handler(sdk.get_agent_mgr()),
        tracer("MyAgent") {
      tracer.trace0("Agent constructed");
   }

   void on_initialized() {
      tracer.trace0("Initialized");
      std::string name = get_agent_mgr()->agent_option("name");
      get_agent_mgr()->status_set("Initialized", "OK");
   }

   void on_agent_option(std::string const & option_name,
                        std::string const & value) {
      tracer.trace3("Option '%s' was set to '%s'", option_name.c_str(),
                    value.c_str());
   }

  //  void on_oper_status(eos::intf_id_t intf, eos::oper_status_t os) {
  //     // do your stuff.. send an email? post to twitter?
  //  }
};

int main(int argc, char ** argv) {
   eos::sdk sdk;
   SkeletonAgent agent(sdk);
   sdk.main_loop(argc, argv);
}
