loop14:
while(true)
{
   while(true)
   {
      if(!ord("\x0b"))
      {
         if(!ord("\x0b"))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 or _temp_1))
      {
         break;
      }
      break loop14;
   }
   §§goto(addr16d8c);
}
var _loc1_;
if(ord("\x03"))
{
   loop16:
   while(true)
   {
      §§push(dofus["\x18\x03\x17"].gapi.ui);
      §§push("SpellForget");
      if(!getTimer())
      {
         §§push(getProperty(§§pop(), _X));
         function(§\x19\x12\x1d§)
         {
            this._btnValidate.enabled = true;
         }
         if(false)
         {
            var §§pop() = §§pop();
            addr1712c:
            loop17:
            while(true)
            {
               loop18:
               while(true)
               {
                  loop19:
                  while(true)
                  {
                     function()
                     {
                        this["\x16\x01\x0e"]({object:this,method:this["\x15\x1e\b"]});
                        §§push({object:this,method:this["\x18\n\x1c"]});
                        §§push(1);
                        §§push(this);
                        §§push("\x16\x01\x0e");
                        if(false)
                        {
                           §§pop() implements ;
                        }
                        §§pop()[§§pop()]();
                        this["\x16\x01\x0e"]({object:this,method:this["\x18\t\x1b"]});
                     }
                     if(!ord("\x0b"))
                     {
                        var §§pop() = §§pop();
                        addr171bf:
                        §§pop()[§§pop()] = new §\§\§pop()§();
                        §§push(dofus["\x18\x03\x17"].gapi);
                        §§push("ui");
                        if(false)
                        {
                           setProperty(§§pop(), _X, §§pop());
                           function(§\x19\x12\x1d§)
                           {
                              var _loc3_;
                              loop1:
                              switch(§\x19\x12\x1d§.target)
                              {
                                 case this._btnValidate:
                                    while(true)
                                    {
                                       §§push(_loc3_ = dofus["\x17\x05\x03"]["\x1b\x06\t"](this["\x1d\x07\x04"].selectedItem));
                                       if(!ord("\x03"))
                                       {
                                          setProperty(§§pop(), _X, §§pop());
                                       }
                                       else
                                       {
                                          addr1726a:
                                          §§pop();
                                          §§push({name:"SpellForget",listener:this,params:{spell:_loc3_}});
                                          §§push("CAUTION_YESNO");
                                          §§push([_loc3_.name]);
                                          §§push("SPELL_FORGET_CONFIRM");
                                          §§push(2);
                                          §§push(this.api.lang);
                                          §§push("getText");
                                          if(false)
                                          {
                                             §§pop()[§§pop()] = §§pop();
                                             break loop1;
                                          }
                                       }
                                       §§goto(addr17302);
                                    }
                                    §§goto(addr1733b);
                                 default:
                                    §§push(_loc0_);
                                    §§push(this);
                                    §§push("_btnCancel");
                                    if(getTimer() + 1)
                                    {
                                       break;
                                    }
                                    §§goto(addr1722e);
                                    §§push(getProperty(§§pop(), _X));
                                 case this._btnClose:
                                    §§goto(addr1723b);
                              }
                              while(true)
                              {
                                 if(§§pop() !== §§pop()[§§pop()])
                                 {
                                    return;
                                 }
                                 addr1723b:
                                 §§push(-1);
                                 §§push(1);
                                 §§push(this.api["\x19\x06\x1c"].Spells);
                                 §§push("\x1b\x06\f");
                                 if(false)
                                 {
                                    §§goto(addr1726a);
                                    §§push(getProperty(§§pop(), _X));
                                 }
                                 addr1733b:
                                 §§pop()[§§pop()]();
                                 this["\x1b\x13\x14"]();
                                 return;
                              }
                              addr17302:
                              §§push(§§pop()[§§pop()]());
                              §§push(this.api.lang.getText("SPELL_FORGET"));
                              §§push(4);
                              §§push(this.api);
                              §§push("\x18\x12\x03");
                              if(false)
                              {
                                 setProperty(§§pop(), _X, §§pop());
                                 break loop2;
                              }
                              addr1722e:
                              §§pop()[§§pop()]["\x1a\x1e\x0e"]();
                           }
                           if(!(getTimer() + 1))
                           {
                              duplicateMovieClip(§§pop(),§§pop(),§§pop());
                              function()
                              {
                                 this["\x1e\x10\t"].title = this.api.lang.getText("SPELL_FORGET");
                                 loop1:
                                 while(true)
                                 {
                                    §§push(this["\x1c\x1b\x0f"]);
                                    §§push("text");
                                    §§push("SPELLS_SHORTCUT");
                                    §§push(1);
                                    §§push(this);
                                    §§push("api");
                                    if(!ord("\x07"))
                                    {
                                       §§push(getProperty(§§pop(), _X));
                                       while(true)
                                       {
                                          §§pop()[§§pop()] = §§pop()[§§pop()]();
                                          this._btnValidate.label = this.api.lang.getText("VALIDATE");
                                          §§push(this._btnCancel);
                                          §§push("label");
                                          §§push("CANCEL_SMALL");
                                          §§push(1);
                                          §§push(this);
                                          §§push("api");
                                          if(getTimer())
                                          {
                                             break loop1;
                                          }
                                          §§pop()[§§pop()] = §§pop();
                                       }
                                       break;
                                       addr173ae:
                                    }
                                    §§pop()[§§pop()] = §§pop()[§§pop()].lang.getText();
                                    §§push(this["\x1c\x1a\x07"]);
                                    §§push("text");
                                    §§push("LEVEL");
                                    §§push(1);
                                    §§push(this.api.lang);
                                    §§push("getText");
                                    §§goto(addr173ae);
                                    setProperty(§§pop(), _X, §§pop());
                                    break;
                                 }
                                 §§pop()[§§pop()] = §§pop()[§§pop()].lang.getText();
                              }
                              if(!getTimer())
                              {
                                 §§push(getProperty(§§pop(), _X));
                                 loop10:
                                 while(true)
                                 {
                                    while(true)
                                    {
                                       while(true)
                                       {
                                          while(true)
                                          {
                                             while(true)
                                             {
                                                if(!§§pop()[§§pop()].gapi)
                                                {
                                                   §§push(_global.dofus["\x18\x03\x17"]);
                                                   §§push("gapi");
                                                   §§push(0);
                                                   §§push("Object");
                                                   if(!(getTimer() + 1))
                                                   {
                                                      var §§pop() = §§pop();
                                                      while(true)
                                                      {
                                                         §§pop()[§§pop()] = §§pop();
                                                         §§push(_loc1_);
                                                         §§push("\x18\t\x1b");
                                                         if(false)
                                                         {
                                                            §§pop() extends §§pop();
                                                            §§goto(addr17490);
                                                         }
                                                         §§goto(addr16f08);
                                                      }
                                                      break loop16;
                                                      addr1747c:
                                                   }
                                                   §§goto(addr171bf);
                                                }
                                                §§goto(addr171c1);
                                             }
                                             §§goto(addr17358);
                                          }
                                          §§goto(addr17070);
                                       }
                                       while(true)
                                       {
                                       }
                                       function()
                                       {
                                          §§push(eval("{invalid_utf8=164}")[§§constant(1)][§§constant(2)][§§constant(3)][§§constant(4)][§§constant(11)]);
                                          §§push(false);
                                          §§push(2);
                                          §§push(super);
                                          §§push(§§constant(10));
                                          if(false)
                                          {
                                             §§push(§§pop()(§§pop()));
                                          }
                                          §§pop()[§§pop()]();
                                       }
                                       while(true)
                                       {
                                          break loop29;
                                          startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
                                          §§goto(addr16e84);
                                       }
                                       break loop17;
                                    }
                                    §§push(getProperty(§§pop(), _X));
                                    loop3:
                                    while(true)
                                    {
                                       loop27:
                                       while(true)
                                       {
                                          if(!§§pop()[§§pop()])
                                          {
                                             §§push(eval(§§constant(5))["{invalid_utf8=164}"][§§constant(1)][§§constant(2)]);
                                             §§push(§§constant(3));
                                             §§push(0);
                                             §§push(§§constant(6));
                                             if(!ord("\n"))
                                             {
                                                §§push(new §\§\§pop()§());
                                                loop4:
                                                while(true)
                                                {
                                                   §§pop() extends §§pop()[§§pop()][§§constant(8)];
                                                   _loc1_ = §§pop()[§§pop()] = §§pop()[§§constant(9)];
                                                   §§push(_loc1_);
                                                   §§push(§§constant(10));
                                                   if(false)
                                                   {
                                                      §§push(new §\§\§pop()§());
                                                      while(true)
                                                      {
                                                      }
                                                      function()
                                                      {
                                                         var _loc2_ = this[§§constant(30)][§§constant(41)][§§constant(42)][§§constant(43)];
                                                         var _loc4_;
                                                         var _loc0_;
                                                         var _loc3_;
                                                         loop3:
                                                         while(true)
                                                         {
                                                            §§push(0);
                                                            §§push(eval(§§constant(44)));
                                                            §§push(§§constant(45));
                                                            if(false)
                                                            {
                                                               setProperty(§§pop(), _X, §§pop());
                                                               do
                                                               {
                                                                  §§push(§§pop()[§§pop()] > 1);
                                                                  var _temp_1;
                                                                  do
                                                                  {
                                                                     if(§§pop())
                                                                     {
                                                                        _loc3_[§§constant(50)](_loc4_);
                                                                     }
                                                                     addr16f97:
                                                                     while((_loc0_ = §§pop()) == null)
                                                                     {
                                                                        §§push(this);
                                                                        §§push(§§constant(26));
                                                                        break loop3;
                                                                        var §§pop() = §§pop();
                                                                     }
                                                                  }
                                                                  while(var §§constant(47) = _loc0_, §§push(_loc2_), §§push(§§constant(47)), if(!getTimer())
                                                                  {
                                                                     §§pop()[§§pop()] = §§pop();
                                                                  }, _loc4_ = §§pop()[eval(§§pop())], var _temp_1 = _loc4_[§§constant(48)] != -1, §§push(_temp_1), !_temp_1);
                                                                  §§pop();
                                                                  §§push(_loc4_);
                                                                  §§push(§§constant(49));
                                                               }
                                                               while(true);
                                                               §§pop() implements ;
                                                               break;
                                                            }
                                                            _loc3_ = new §§pop()[§§pop()][§§constant(46)]();
                                                            §§goto(addr16f97);
                                                         }
                                                         §§pop()[§§pop()][§§constant(51)] = _loc3_;
                                                         §§enumerate(_loc2_);
                                                      }
                                                      while(true)
                                                      {
                                                         if(false)
                                                         {
                                                            §§push(getProperty(§§pop(), _X));
                                                            continue loop23;
                                                         }
                                                         §§pop()[§§pop()] = §§pop();
                                                         §§push(_loc1_);
                                                         §§push(§§constant(25));
                                                         if(!(getTimer() + 1))
                                                         {
                                                            §§push(§§pop()(§§pop()));
                                                            while(true)
                                                            {
                                                               §§pop()[§§pop()] = §§pop();
                                                               §§push(_loc1_);
                                                               §§push(§§constant(15));
                                                               if(!ord("\x07"))
                                                               {
                                                                  §§pop()[§§pop()] = §§pop();
                                                                  break loop27;
                                                               }
                                                               addr17533:
                                                               function()
                                                               {
                                                                  this[§§constant(19)][§§constant(20)] = false;
                                                                  this[§§constant(22)][§§constant(23)](§§constant(21),this);
                                                                  §§push(this);
                                                                  §§push(§§constant(21));
                                                                  §§push(2);
                                                                  §§push(this[§§constant(24)]);
                                                                  §§push(§§constant(23));
                                                                  if(false)
                                                                  {
                                                                     §§push(new §\§\§pop()§());
                                                                  }
                                                                  §§pop()[§§pop()]();
                                                                  this[§§constant(19)][§§constant(23)](§§constant(21),this);
                                                                  this[§§constant(26)][§§constant(23)](§§constant(25),this);
                                                               }
                                                               if(ord("\x02"))
                                                               {
                                                                  while(true)
                                                                  {
                                                                     §§pop()[§§pop()] = §§pop();
                                                                     §§push(_loc1_);
                                                                     §§push("\x18\n\x1c");
                                                                     if(false)
                                                                     {
                                                                        §§pop() implements ;
                                                                        addr174a4:
                                                                        §§push(§§pop()[§§pop()] = §§pop());
                                                                        §§push(eval("{invalid_utf8=164}")[§§constant(1)][§§constant(2)]);
                                                                        §§push(§§constant(7));
                                                                        if(false)
                                                                        {
                                                                           §§push(getProperty(§§pop(), _X));
                                                                           break loop22;
                                                                        }
                                                                        continue loop4;
                                                                     }
                                                                     §§goto(addr17358);
                                                                  }
                                                                  break loop16;
                                                               }
                                                               setProperty(§§pop(), _X, §§pop());
                                                               §§goto(addr175c6);
                                                               break loop19;
                                                            }
                                                            break loop16;
                                                         }
                                                         §§goto(addr17100);
                                                      }
                                                      break loop16;
                                                   }
                                                   break loop25;
                                                }
                                                break loop16;
                                             }
                                             §§pop()[§§pop()] = new §\§\§pop()§();
                                          }
                                          §§push(eval(§§constant(5))["{invalid_utf8=164}"][§§constant(1)]);
                                          §§push(§§constant(2));
                                          if(false)
                                          {
                                             §§pop() extends §§pop();
                                             while(!§§pop()[§§pop()])
                                             {
                                                if(!eval("{invalid_utf8=164}"))
                                                {
                                                   §§push(§§constant(5));
                                                   if(false)
                                                   {
                                                      §§push(§§pop()(§§pop()));
                                                      while(true)
                                                      {
                                                         §§pop()[§§pop()] = §§pop();
                                                         §§push(_loc1_);
                                                         §§push(§§constant(66));
                                                         if(false)
                                                         {
                                                            var §§pop() = §§pop();
                                                            addr17070:
                                                            §§pop()[§§pop()] = §§pop();
                                                            §§push(_loc1_);
                                                            §§push(§§constant(12));
                                                            if(false)
                                                            {
                                                               §§pop() extends §§pop();
                                                               break loop10;
                                                            }
                                                            break loop19;
                                                         }
                                                         addr16d8c:
                                                         while(true)
                                                         {
                                                         }
                                                         function(§\x19\x12\x1d§)
                                                         {
                                                            var _loc0_;
                                                            var _loc3_;
                                                            if((_loc0_ = §\x19\x12\x1d§[§§constant(52)][§§constant(67)]) === §§constant(68))
                                                            {
                                                               §§push(§\x19\x12\x1d§);
                                                               §§push(§§constant(52));
                                                               if(false)
                                                               {
                                                                  startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
                                                               }
                                                               _loc3_ = §§pop()[§§pop()][§§constant(57)][§§constant(58)];
                                                               §§push(_loc3_[§§constant(69)]);
                                                               §§push(1);
                                                               §§push(this[§§constant(30)][§§constant(63)]);
                                                               §§push(§§constant(43));
                                                               if(!getTimer())
                                                               {
                                                                  §§pop() extends §§pop();
                                                               }
                                                               §§pop()[§§pop()][§§constant(64)]();
                                                               this[§§constant(65)]();
                                                            }
                                                         }
                                                         while(false)
                                                         {
                                                            setProperty(§§pop(), _X, §§pop());
                                                            break loop25;
                                                         }
                                                         break loop16;
                                                      }
                                                      break loop18;
                                                      addr1705c:
                                                   }
                                                   break loop22;
                                                }
                                                break loop23;
                                             }
                                             break loop17;
                                             break loop16;
                                             addr17036:
                                          }
                                          break;
                                       }
                                       while(true)
                                       {
                                          §§push(§§pop()[§§pop()][§§constant(3)]);
                                          §§push(§§constant(4));
                                          if(!ord("\x0b"))
                                          {
                                             §§goto(addr17533);
                                             §§push(§§pop()(§§pop()));
                                          }
                                          while(true)
                                          {
                                          }
                                          function()
                                          {
                                             super();
                                          }
                                          while(true)
                                          {
                                             if(false)
                                             {
                                                §§push(§§pop()());
                                                continue loop3;
                                             }
                                             §§goto(addr174a4);
                                          }
                                          break loop16;
                                       }
                                       §§goto(addr17070);
                                    }
                                    break loop16;
                                 }
                                 while(!§§pop())
                                 {
                                    eval(§§constant(5))["{invalid_utf8=164}"][§§constant(1)] = new §\§\§constant(6)§();
                                 }
                                 §§push(eval("{invalid_utf8=164}"));
                                 §§push(§§constant(1));
                                 if(false)
                                 {
                                    break loop18;
                                 }
                              }
                              §§goto(addr1747c);
                           }
                           §§goto(addr1705c);
                        }
                        break loop20;
                     }
                     §§goto(addr17505);
                  }
                  §§goto(addr1712c);
               }
               startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
               break loop16;
            }
            return;
         }
         continue loop23;
      }
      §§goto(addr17036);
   }
   break loop3;
}
§§goto(addr177c0);
