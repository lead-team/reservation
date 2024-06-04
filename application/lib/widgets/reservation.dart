// ignore_for_file: public_member_api_docs, sort_constructors_first
import 'package:application/design/food.dart';
import 'package:application/design/meal.dart';
import 'package:application/design/shift.dart';
import 'package:application/design/shiftmeal.dart';
import 'package:application/gen/assets.gen.dart';
import 'package:application/repository/HttpClient.dart';
import 'package:application/repository/tokenManager.dart';
import 'package:application/widgets/profile.dart';
import 'package:choice/choice.dart';
import 'package:dio/dio.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:persian_datetime_picker/persian_datetime_picker.dart';

class ReservePage extends StatefulWidget {
  @override
  _ReservePageState createState() => _ReservePageState();
}

class _ReservePageState extends State<ReservePage> {
  Jalali? selectedDate;
  String? myShiftName;
  bool selectedDateForMeal = false;
  bool selectedShiftForMeal = false;

  Future<List<ShiftMeal>> getMenu(String? shiftName) async {
    VerifyToken? verifyToken = await TokenManager.verifyAccess(context);
    if (verifyToken == VerifyToken.verified) {
      String? myAccess = await TokenManager.getAccessToken();
      final response = await HttpClient.instance.post('api/get-menu/',
          data: {
            "date": selectedDate!.toJalaliDateTime().substring(0, 10),
            'shift': shiftName
          },
          options: Options(headers: {'Authorization': 'JWT $myAccess'}));
      List<ShiftMeal> myShiftMeals = [];
      
        for (var i in response.data) {
          Food food1 = Food(
              id: i["meal"]["food"]["id"],
              name: i["meal"]["food"]["name"],
              type: i["meal"]["food"]["type"]);
          Food? diet;
          if (i["meal"]["diet"] == null) {
            diet = null;
          } else {
            diet = Food(
                id: i["meal"]["diet"]["id"],
                name: i["meal"]["diet"]["name"],
                type: i["meal"]["diet"]["type"]);
          }
          Food? dessert;
          if (i["meal"]["dessert"] == null) {
            dessert = null;
          } else {
            dessert = Food(
                id: i["meal"]["dessert "]["id"],
                name: i["meal"]["dessert"]["name"],
                type: i["meal"]["dessert"]["type"]);
          }
          Meal myMeal = Meal(
              id: i["meal"]["id"],
              food: food1,
              diet: diet,
              desert: dessert,
              dailyMeal: i["meal"]["daily_meal"]);
          Shift myShift =
              Shift(id: i["shift"]["id"], shiftName: i["shift"]["shift_name"]);
          ShiftMeal temp = ShiftMeal(
              id: i["id"], date: i["date"], meal: myMeal, shift: myShift);
          //print("Success");
          myShiftMeals.add(temp);
        
      }
      return myShiftMeals;
    }
    return [];
  }

  List<String> choices = ['A', 'B', 'C', 'D'];

  String? selectedValue;

  void setSelectedValue(String? value) {
    setState(() {
      selectedShiftForMeal = false;
    });
    setState(() {
      selectedValue = value;
      myShiftName = value;
      selectedShiftForMeal = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          foregroundColor: Colors.white,
          title: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              IconButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  icon: const Icon(
                    CupertinoIcons.back,
                    size: 40,
                    color: Color.fromARGB(255, 2, 16, 43),
                  )),
              Text(
                'صفحه ی رزرو',
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium!
                    .copyWith(fontSize: 25, fontWeight: FontWeight.bold),
              ),
              IconButton(
                  onPressed: () {
                    //Navigator.pushReplacement(context, MyHomePage(title: ''));
                  },
                  icon: const Icon(
                    CupertinoIcons.mail,
                    size: 40,
                    color: Color.fromARGB(255, 2, 16, 43),
                  )),
            ],
          ),
          backgroundColor: Colors.white,
        ),
        body: SafeArea(
            child: Stack(fit: StackFit.expand, children: [
          Container(
            decoration: const BoxDecoration(
              //color: Colors.white,
              image: DecorationImage(
                image: AssetImage('assets/pintrest2.jpg'),
                fit: BoxFit
                    .cover, // This ensures the image covers the entire background
              ),
            ),
            child: Padding(
              padding: EdgeInsets.fromLTRB(
                  0, 0, 0, MediaQuery.of(context).size.height * 0.62),
              child: Container(
                decoration: const BoxDecoration(
                    color: Colors.white,
                    boxShadow: const [BoxShadow(blurRadius: 2)],
                    borderRadius: BorderRadius.only(
                        bottomLeft: Radius.circular(24),
                        bottomRight: Radius.circular(24))),
                width: MediaQuery.of(context).size.width,
                height: MediaQuery.of(context).size.height * 0.35,
                child: Column(children: [
                  const SizedBox(
                    height: 15,
                  ),
                  Text(
                    "Select your shift and your desired date :",
                    style: Theme.of(context)
                        .textTheme
                        .titleLarge!
                        .copyWith(fontSize: 18),
                  ),
                  Choice<String>.inline(
                    clearable: false,
                    value: ChoiceSingle.value(selectedValue),
                    onChanged: ChoiceSingle.onChanged(setSelectedValue),
                    itemCount: choices.length,
                    itemBuilder: (state, i) {
                      return ChoiceChip(
                        selected: state.selected(choices[i]),
                        onSelected: state.onSelected(choices[i]),
                        label: Text(choices[i]),
                      );
                    },
                    listBuilder: ChoiceList.createScrollable(
                      spacing: 10,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 25,
                      ),
                    ),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      const SizedBox(),
                      ElevatedButton(
                          onPressed: _pickDate,
                          style: ElevatedButton.styleFrom(
                              minimumSize: Size(
                                  MediaQuery.of(context).size.width * 0.4, 45),
                              backgroundColor: Colors.black26,
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16))),
                          child: Text("Select date",
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyLarge!
                                  .copyWith(
                                      fontSize: 20,
                                      fontWeight: FontWeight.w500,
                                      color: Colors.white))),
                      Text(
                        selectedDate == null
                            ? "no date selected"
                            : selectedDate!.toJalaliDateTime().substring(0, 10),
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      const SizedBox()
                    ],
                  )
                ]),
              ),
            ),
          ),
          selectedDateForMeal && selectedShiftForMeal
              ? Padding(
                  padding: EdgeInsets.fromLTRB(
                      0, MediaQuery.of(context).size.height * 0.28, 0, 0),
                  child: foodListBuilder(),
                )
              : const Center(child: CircularProgressIndicator())
        ])));
  }

  FutureBuilder<List<ShiftMeal>> foodListBuilder() {
    return FutureBuilder<List<ShiftMeal>>(
        future: getMenu(myShiftName),
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return const Center(
              child: SizedBox(height: 10, child: Text("Something went wrong!")),
            );
          } else if (snapshot.connectionState == ConnectionState.waiting) {
            return Center(child: const CircularProgressIndicator());
          } else if (snapshot.hasData) {
            print(snapshot.data);
            print(snapshot.data!.length);
            if (snapshot.data!.isEmpty) {
              return Center(
                child: Text(
                  "There is no food available!",
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge!
                      .copyWith(color: Colors.white),
                ),
              );
            }
            return ReserveList(myMeal: snapshot.data!);
          } else {
            return const Center(
              child: SizedBox(height: 10, child: Text("Something went wrong!")),
            );
          }
        });
  }

  Future<void> _pickDate() async {
    Jalali? pickedDate = await showPersianDatePicker(
      context: context,
      initialDate: selectedDate ?? Jalali.now(),
      firstDate: Jalali(1385, 8),
      lastDate: Jalali(1450, 9),
    );

    if (pickedDate != null && pickedDate != selectedDate) {
      setState(() {
        selectedDateForMeal = false;
      });
      setState(() {
        selectedDate = pickedDate;
        selectedDateForMeal = true;
      });
    }
  }
}

class ReserveList extends StatefulWidget {
  ReserveList({
    Key? key,
    required this.myMeal,
  }) : super(key: key);
  final List<ShiftMeal> myMeal;
  @override
  State<ReserveList> createState() => _ReserveListState(myList: myMeal);
}

class _ReserveListState extends State<ReserveList> {
  int selectedIndex = -1;
  final List<ShiftMeal> myList;

  _ReserveListState({required this.myList});

  @override
  Widget build(BuildContext context) {
    print(myList.length);
    return Expanded(
      child: ListView.builder(
          itemCount: myList.length,
          itemBuilder: (context, index) {
            //print(snapshot.data![index]);
            return Padding(
              padding: const EdgeInsets.all(16.0),
              child: InkWell(
                onTap: () {
                  setState(() {
                    selectedIndex = index;
                  });
                },
                child: Container(
                  width: MediaQuery.of(context).size.width,
                  height: selectedIndex == index
                      ? MediaQuery.of(context).size.height * (1 / 3)
                      : 75,
                  decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(16),
                      color: Colors.white60,
                      boxShadow: const [BoxShadow(blurRadius: 4)]),
                  child: Padding(
                    padding: selectedIndex == index
                        ? const EdgeInsets.all(32)
                        : const EdgeInsets.all(16.0),
                    child: selectedIndex == index
                        ? _columnMethod(
                            myList!,
                            index,
                            context,
                          )
                        : _rowMethod(
                            myList!,
                            index,
                            context,
                          ),
                  ),
                ),
              ),
            );
          }),
    );
  }

  Column _columnMethod(
      List<ShiftMeal> shiftMeal, int index, BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              TextButton(
                  onPressed: () {
                    setState(() {
                      if (selectedIndex != index) {
                        selectedIndex = index;
                      } else {
                        selectedIndex = -1;
                      }
                    });
                  },
                  child: Text(
                    'Shift : ${shiftMeal[index].shift.shiftName}',
                    style: Theme.of(context)
                        .textTheme
                        .titleLarge!
                        .copyWith(fontSize: 24, fontWeight: FontWeight.bold),
                  )),
              TextButton(
                  onPressed: () {},
                  child: Text(
                      'foods: ${shiftMeal[index].meal.food.name}',
                      style: Theme.of(context).textTheme.titleLarge!.copyWith(
                          fontSize: 19, fontWeight: FontWeight.w300))),
              const SizedBox(
                height: 6,
              ),
              Text(
                  shiftMeal[index].meal.diet == null
                      ? 'diet: no diet food available'
                      : 'diet: ${shiftMeal[index].meal.diet!.name}',
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge!
                      .copyWith(fontSize: 19, fontWeight: FontWeight.w300)),
              const SizedBox(
                height: 8,
              ),
              Text(
                  shiftMeal[index].meal.desert == null
                      ? 'dessert: no dessert food available'
                      : 'dessert: ${shiftMeal[index].meal.desert!.name}',
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge!
                      .copyWith(fontSize: 19, fontWeight: FontWeight.w300)),
              const SizedBox(
                height: 8,
              ),
              Text(shiftMeal[index].date,
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge!
                      .copyWith(fontSize: 19, fontWeight: FontWeight.w300)),
            ],
          ),
        )
      ],
    );
  }

  Row _rowMethod(List<ShiftMeal> shiftMeals, int index, BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        Text(shiftMeals[index].shift.shiftName,
            style:
                Theme.of(context).textTheme.bodyLarge!.copyWith(fontSize: 19)),
        Text(
          shiftMeals[index].date,
          style: Theme.of(context).textTheme.bodyLarge!.copyWith(fontSize: 19),
        ),
      ],
    );
  }
}