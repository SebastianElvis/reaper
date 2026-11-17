# Definitions and Composition

You state each applicable security property as a precise predicate, game, simulation definition, or reference to a numbered definition.
You specify quantifiers, parameters, runtime, and probability bounds. A label such as safety or liveness does not determine these details.
You identify a definition that you supply yourself. You do not attribute it to the source paper.

You use the security and composition checks in [methodology.md](methodology.md).
You distinguish standalone security, sequential composition, and the exact concurrent-composition guarantee.
You check shared setup and sessions when another protocol uses the result as a building block.
You record relevant composition limits. You do not require a UC proof for a claim that only concerns standalone security.
