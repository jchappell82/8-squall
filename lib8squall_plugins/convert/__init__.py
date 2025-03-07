# -*- coding: utf-8 -*-
import re

from . import angle
from . import area
from . import energy
from . import force
from . import length
from . import pressure
from . import temperature
from . import timeconv
from . import volume
from . import weight

def get_help_summary(client, message):
    return ("`!conv [quantity] <unit> [to] <unit>` for scale conversion.",)

_QUERY_RE = re.compile(r'(?P<qty>-?\d*\.?\d*)?\s*(?P<unit1>["\'\w]+)\s+(?:to\s+)?(?P<unit2>["\'\w]+)')

def _process(module, quantity, unit1, unit2):
    decoder = module.DECODERS.get(unit1)
    if not decoder:
        return None
    encoder = module.ENCODERS.get(unit2)
    if not encoder:
        return None
        
    (intermediate, normalised_unit1) = decoder(quantity)
    (result, normalised_unit2) = encoder(intermediate)
    return (result, normalised_unit1, normalised_unit2)
    
async def handle_message(client, message):
    if message.content.startswith('!conv '):
        query_match = _QUERY_RE.search(message.content[6:])
        if query_match:
            unit1 = query_match.group('unit1').title()
            unit2 = query_match.group('unit2').title()
            
            quantity = query_match.group('qty')
            if quantity is None or quantity == '.': #the regex allows '.' for the sake of readability
                quantity = 1.0
            else:
                quantity = float(quantity)
                
            for module in (
                temperature,
                length,
                weight,
                volume,
                angle,
                timeconv,
                area,
                energy,
                force,
                pressure,
            ):
                result = _process(module, quantity, unit1, unit2)
                if result:
                    (result, normalised_unit1, normalised_unit2) = result
                    await message.reply("{:,.2f}{} = {:,.2f}{}".format(
                        quantity, normalised_unit1,
                        result, normalised_unit2,
                    ))
                    break
            else:
                await message.reply("No conversion available for {} and {}.".format(unit1, unit2))
        return True
    return False
