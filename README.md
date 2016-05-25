# Advent

Adventure is a port of the classic terminal game
[Colossal Cave Adventure](https://en.wikipedia.org/wiki/Colossal_Cave_Adventure)
to modern chat clients. Adventure is available on both FB messenger
and Telegram.

[![Messenger](https://devinmcgloin.com/public/advent/messenger.png)](https://m.me/adventerm)


[![Telegram](https://devinmcgloin.com/public/advent/telegram.png)](http://telegram.me/cave_adventure_bot)

The content of the game is mostly the same as the original released in
1976, it even runs off the same data file! I have however made a few
necessary changes to how a user interacts with the game:

 * Messages are sent in true case as opposed to the original uppercase.
 * Messages are spaced out in order to make the game feel more natural
   in messaging clients.
 * Info and instruction commands have changed in order to allow people
   to restart the game, and activate other game mechanics that would
   ordinarily be changed in the terminal.

It is built with [Smooch](https://smooch.io) to manage messaging and
deployed on [Heroku](https://heroku.com). Source is avaliable on
[Github](https://github.com/devinmcgloin/advent). Please reach out to
[Devin McGloin](https://twitter.com/devinmcgloin) with any feedback.

## Usage

```
You are standing at the end of a road before a small brick building.
```

```
Around you is a forest.
```

```
A small stream flows out of the building and down a gully.
```


building

```
You are inside a building, a well house for a large spring.
```

```
There are some keys on the ground here.
```

```
There is a shiny brass lamp nearby.
```

```
There is food here.
```

```
There is a bottle of water here.
```

get keys

```
Ok.
```

## Contributions

* Willie Crowther for originally developing the game.
* Don Woods for adding features many of the features of the current
  program.
* [Brandon Rhodes](http://rhodesmill.org/brandon/) for his
  implementation of Colossal Cave Adventure. It can be found on PyPI
  and [Github](https://github.com/brandon-rhodes/python-adventure).
* [Como el buen vino studio](https://thenounproject.com/term/lantern/87141/)
  in Spain for the lantern logo.

### License

[MIT License](http://chibicode.mit-license.org/)
