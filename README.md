# craps-engine

Craps Engine Microservice

A craps microservice designed to take in a game-state, a set of new instructions for placing/removing/toggling bets, and
an optional hash. The engine will then roll the dice based on the hash (if provided) or a randomly generated hash (if
not), and return the new game-state, a list of lost bets(removed from the game-state) a list of won bets (these remain
in the game-state), and a summary.

## Installation

### Docker Install

The Docker image is based off of the AWS Lambda Python image and as such comes with a couple stipulations:

1. When you run the image as a container, be sure to make port `8080` available somewhere on your system. For example,
   with the `-p 9000:8080` flag.
2. The HTTP request to the engine must go to the appropriate path (`/2015-03-31/functions/function/invocations`) in
   order to function. For a `curl` example for the above setting, use
    ```
    curl -XPOST -w '\n' "http://localhost:9000/2015-03-31/functions/function/invocations" --data "@sample-request.json"
    ```

### AWS Lambda Install

1. Zip the contents of the directory (without a root directory) into a file
2. Upload the zip file to your AWS Lambda Python 3.9 function
3. Ensure there is a Layer containing the needed packages outlined in `requirements.txt`

### Python Interpreter

1. Run `python3 -i engine.py`
2. Pass a `json.dump()`'d request object to `process_request(request)`
3. Have Fun

## The Request Object

The Root object contains 3 optional properties: `table`, `instructions`, and `hash`

### `table`

A complex object consisting of `config` (a Craps Table Config Object), `puck_location` (either the point number, or
null (optional if null), and `existing_bets` (an array of Bet Signature Objects)

#### Craps Table Config Object

All you could ever want to configure a craps table.
Defaults can be located in `craps/table/config/__init__.py`.
Specify the odds is a simple as using `mirror345()` (default 3x4x5x odds) or `flat(n)` where n is an integer denoting
the flat odds.
For example, for 2x odds, the odds value would be `flat(2)`.

Odds _must_ be specified if `is_crapless` is set to `true`.

#### Bet Signature Object

The Bet Signature Object consists of two required properties (`type` and `wager`) as well as three optional
properties (`odds`, `placement`, and `override_puck`)

- `type` is the type of Bet, one of
    - `PassLine` - optional integer placement if point has been set
    - `Put` - requires integer placement
    - `Come` - optional integer placement if bet has been moved
    - `DontPass` - optional integer placement if point has been set
    - `DontCome` - optional integer placement if bet has been moved
    - `Field`
    - `Place` - requires integer placement
    - `Buy` - requires integer placement
    - `Lay` - requires integer placement, `override_puck` is `ON` by default
    - `Hardway` - requires integer placement
    - `AnySeven`
    - `AnyCraps`
    - `Hop` - requires placement in the form of `[int, int]` to represent the dice roll
    - `Horn` - requires integer placement
    - `HornHigh` - requires integer placement
    - `World`
    - `Craps3Way`
    - `CE`
- `wager` is an integer value representing the bet - all wagers and payouts are in whole numbers.
- `odds` are an integer value representing a fair odds bet to place/lay with the wager.
- `placement` represents the location on the table for the bet, this will be an integer value for most bets that need
  it, or an array of two integers representing a dice roll for hop bets.
- `override_puck` by default, the bets that can be toggled `ON` and `OFF` follow the puck, but if you would like a
  particular bet to be set to `ON` or `OFF`, you can set it here, a value of `null` will force it to follow the puck.

### Instructions

`instructions` is an object generally consisting of two properties: `place` and `retrieve`. Both of these properties are
an array of Bet Signature Object. The bets listed in `place` will be placed on the table (if allowed), while the items
in `retrieve` will be removed from the table and returned to the player (if allowed).

Bets may have their wager altered with the `update` property. Just list any bets with their new wager in this array.

Odds may be placed on a bet with the `set_odds` property, an array of Bet Signature Objects that include the `odds`
property.

Odds will be removed from bets listed under the `remove_odds` property.

`retrieve`, `set_odds`, and `remove_odds` items need not specify `override_puck`, this value will be ignored if
provided.

Advanced instructions consist of the following properties: `turn_on`, `turn_off`, and `follow_puck`. These are also
arrays of Bet Signature Objects and should _not_ specify the `override_puck`, as each array sets this value for the
whole
group.

If any illegal instructions are provided, the service will return an error.

### `hash`

A SHA-256 hash, the same hash will always yield the same dice roll. Hash is included for Provably Fair applications.
This engine does not keep track of server seed or nonce, this value should be the final hashed value of server seed,
client seed, and nonce

## The Return Object

The return object is also a valid request object and can be fed right back into the service to get the same result.
If no hash was provided in the original request, the random hash used is included in the result.
The result object also has some additional properties not used by the request:

- `winners` is an array of winning bets, including additional details such as win amounts
- `losers` is an array of the losing bets
- `net_table` is an object representing the new state of the table, the puck has been set/removed if needed, and the
  losing bets removed
- `summary` is a summary object including:
    - `dice_outcome` represented as an array of two integers
    - `total_returned_to_player` is the total value from bets taken down by the player
    - `total_winnings_to_player`, a summation of all the winnings the player received (minus any required vig)
    - `value_of_losers` is the total value of all losing bets
    - `value_on_table` is the total value of all bets remaining on the table
    - `value_at_risk` is the total value of all ON bets remaining on the table

## Playing a Game (random rolls)

1. Send in a Request Object:
    - Defining the Table (if other than default) and the `instructions` list.
    - Subtracting the cost of any bets (and pre-payed vig) from the player's bank.
    - Leave off `hash` or set it to `null`.
2. Add the `total_returned_to_player` back to the player's bank.
3. Add the `total_winnings_to_player` to the player's bank.
4. Use the response to build a new request object:
    - set the `table` property to the value of `new_table` from the response
    - set any new `instructions` (Subtracting the cost of any bets (and pre-payed vig) from the player's bank).
    - Leave off `hash` or set it to `null`.
5. Repeat Steps 2-4 until `summary.value_on_table` is `0`; at this point, the player has no bets on the table.

## Playing a Game (Provably Fair)

1. Generate a server seed
2. Send a hash of the server seed to the player
3. Retrieve a client seed from the player
4. Set nonce to 0
5. Generate an SHA-256 hash from the server seed, the client seed, and the nonce
6. Send in a Request Object:
    - Defining the Table (if other than default) and the `instructions` list.
    - Subtracting the cost of any bets (and pre-payed vig) from the player's bank.
    - Setting `hash` to the value of the hash generated in step 5.
7. Add the `total_returned_to_player` back to the player's bank.
8. Add the `total_winnings_to_player` to the player's bank.
9. Increment the nonce by 1
10. Use the response to build a new request object:
    - set the `table` property to the value of `new_table` from the response
    - set any new `instructions` (Subtracting the cost of any bets (and pre-payed vig) from the player's bank).
    - Leave off `hash` or set it to `null`.
11. Repeat Steps 5-10 until `summary.value_on_table` is `0`; at this point, the player has no bets on the table.
12. At this point (and only this point) you may reveal the server seed to the player.
