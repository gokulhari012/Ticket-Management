char *keyLookupTable[128] = {
"END",  //keycode: 0
"NA", //keycode: 1
"NA", //keycode: 2
"NA", //keycode: 3
"a",  //keycode: 4
"b",  //keycode: 5
"c",  //keycode: 6
"d",  //keycode: 7
"e",  //keycode: 8
"f",  //keycode: 9
"g",  //keycode: 10
"h",  //keycode: 11
"i",  //keycode: 12
"j",  //keycode: 13
"k",  //keycode: 14
"l",  //keycode: 15
"m",  //keycode: 16
"n",  //keycode: 17
"o",  //keycode: 18
"p",  //keycode: 19
"q",  //keycode: 20
"r",  //keycode: 21
"s",  //keycode: 22
"t",  //keycode: 23
"u",  //keycode: 24
"v",  //keycode: 25
"w",  //keycode: 26
"x",  //keycode: 27
"y",  //keycode: 28
"z",  //keycode: 29
"1",  //keycode: 30
"2",  //keycode: 31
"3",  //keycode: 32
"4",  //keycode: 33
"5",  //keycode: 34
"6",  //keycode: 35
"7",  //keycode: 36
"8",  //keycode: 37
"9",  //keycode: 38
0,  //keycode: 39
"NA", //keycode: 40
"ESC" ,//keycode: 41
"Backspace", //keycode: 42
"TAB", //keycode: 43
"Space", //keycode: 44
"-/_", //keycode: 45
"+/=" ,//keycode: 46
"[/{", //keycode: 47
"]/}", //keycode: 48
"\\/|" ,//keycode: 49
"NA", //keycode: 50
"NA", //keycode: 51
"NA", //keycode: 52
"`", //keycode: 53
"NA" ,//keycode: 54
"NA" ,//keycode: 55
"NA", //keycode: 56
"CAP_Lock", //keycode: 57
"F1", //keycode: 58
"F2" ,//keycode: 59
"F3", //keycode: 60
"F4", //keycode: 61
"F5" ,//keycode: 62
"F6" ,//keycode: 63
"F7" ,//keycode: 64
"F8", //keycode: 65
"F9" ,//keycode: 66
"F10" ,//keycode: 67
"F11", //keycode: 68
"F12", //keycode: 69
"NA" ,//keycode: 70
"NA", //keycode: 71
"NA", //keycode: 72
"NA", //keycode: 73
"NA" ,//keycode: 74
"NA", //keycode: 75
"NA", //keycode: 76
"NA", //keycode: 77
"NA", //keycode: 78
"NA", //keycode: 79
"NA", //keycode: 80
"NA", //keycode: 81
"NA", //keycode: 82
"NUM_Lock", //keycode: 83
"/", //keycode: 84
"*", //keycode: 85
"-", //keycode: 86
"+", //keycode: 87
"NUM_Enter", //keycode: 88
"1/NUM_End", //keycode: 89
"2/NUM_Down", //keycode: 90
"3/NUM_Pagedown", //keycode: 91
"4/NUM_LEFT", //keycode: 92
"5", //keycode: 93
"6/NUM_Right", //keycode: 94
"7/NUM_Home", //keycode: 95
"8/NUM_UP", //keycode: 96
"9/NUM_Pageup", //keycode: 97
"0/NUM_Ins",  //keycode: 98
"./NUM_Del",  //keycode: 99
"NA", //keycode: 100
"NA" ,//keycode: 101
"NA", //keycode: 102
"NA" ,//keycode: 103
"NA" ,//keycode: 104
"NA" ,//keycode: 105
"NA" ,//keycode: 106
"NA" ,//keycode: 107
"NA" ,//keycode: 108
"NA" ,//keycode: 109
"NA" ,//keycode: 110
"NA" ,//keycode: 111
"NA" ,//keycode: 112
"NA" ,//keycode: 113
"NA" ,//keycode: 114
"NA" ,//keycode: 115
"NA" ,//keycode: 116
"NA" ,//keycode: 117
"NA" ,//keycode: 118
"NA" ,//keycode: 119
"NA" ,//keycode: 120
"NA" ,//keycode: 121
"NA" ,//keycode: 122
"NA" ,//keycode: 123
"NA" ,//keycode: 124
"NA" ,//keycode: 125
"NA" ,//keycode: 126
"NA" //keycode: 127
};

// Special and Modifier Keys
const char* keyModifierLookup[8] = {
  "",     // 0x00 No modifier
  "Left Ctrl",    // 0x01 Left Control
  "Left Shift",   // 0x02 Left Shift
  "Left Alt",     // 0x03 Left Alt
  "Left GUI",     // 0x04 Left GUI (Windows/Command key)
  "Right Ctrl",   // 0x05 Right Control
  "Right Shift",  // 0x06 Right Shift
  "Right Alt",    // 0x07 Right Alt
};
