#include "doc_utils.h"

#include "option_parser.h"
#include "predefinitions.h"

using namespace std;

namespace options {
void PluginInfo::fill_docs(Registry &registry) {
    OptionParser parser(key, registry, Predefinitions(), true, true);
    doc_factory(parser);
}

string PluginInfo::get_type_name(const Registry &registry) const {
    return type_name_factory(registry);
}
}
