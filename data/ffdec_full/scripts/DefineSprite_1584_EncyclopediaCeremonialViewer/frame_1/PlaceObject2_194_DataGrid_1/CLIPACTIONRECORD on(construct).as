on(construct){
   loop4:
   while(true)
   {
      loop5:
      while(true)
      {
         if(!(0x2F2001B8 & 0x2F2001B8))
         {
            if(!ord("\x06"))
            {
               while(true)
               {
                  eval(§§pop())[5] = 25;
                  eval("")[6] = 26;
                  set("",true);
                  §§push("\x07\x19");
                  §§push(false);
                  if(!getTimer())
                  {
                     §§goto(addr17991);
                     §§push(§§pop()(§§pop()));
                  }
                  §§goto(addr17a45);
                  break loop5;
               }
               §§goto(addr17a44);
               addr17958:
            }
         }
         else
         {
            §§push(799955741);
         }
         if(!§§pop())
         {
            break;
         }
         break loop4;
      }
      §§pop()[§§pop()] = §§pop();
      §§goto(addr17958);
   }
   addr17ae7:
   cellRenderer = "EncyclopediaEquipmentsViewerEquipment";
   set("\x16\x1d\x1b",[]);
   eval("\x16\x1d\x1b")[0] = "\x18\x02\x1d";
   while(true)
   {
      §§push(eval("\x16\x1d\x1b"));
      §§push(1);
      §§push("searchName");
      if(!getTimer())
      {
         §§pop() extends §§pop();
         while(true)
         {
            eval(§§pop())[2] = 40;
            eval(§§constant(10))[3] = 80;
            §§push(eval(§§constant(10)));
            §§push(4);
            §§push(40);
            break loop5;
            §§pop() extends §§pop();
            §§goto(addr17ae7);
            §§pop() extends §§pop();
         }
         addr17bae:
         addr17bad:
         getProperty(§§pop(), _X);
         return;
         addr17aa5:
      }
      loop2:
      while(true)
      {
         §§pop()[§§pop()] = §§pop();
         eval("{invalid_utf8=157}\x01{invalid_utf8=136}\t")[2] = "7";
         eval("{invalid_utf8=157}\x01{invalid_utf8=136}\t")[3] = "{invalid_utf8=147}";
         §§push("{invalid_utf8=157}\x01{invalid_utf8=136}\t");
         if(!ord("\n"))
         {
            addr17a0a:
            set(§§pop(),getProperty(§§pop(), _X));
            eval("")[0] = 40;
            eval("")[1] = 125;
            §§push("");
            if(!ord("\x06"))
            {
               break;
            }
            §§goto(addr17aa5);
         }
         addr17991:
         while(true)
         {
            eval(§§pop())[4] = "O{invalid_utf8=150}\x02";
            eval("{invalid_utf8=157}\x01{invalid_utf8=136}\t")[5] = "\b\n\x1c{invalid_utf8=150}\n";
            eval("{invalid_utf8=157}\x01{invalid_utf8=136}\t")[6] = "\x07\x05";
            §§push("");
            §§push([]);
            if(false)
            {
               §§pop()[§§pop()] = §§pop();
               continue loop2;
            }
            §§goto(addr17a0a);
            continue loop2;
         }
         break loop5;
      }
      addr17a44:
      §§pop()[§§pop()] = §§pop();
      break;
   }
   addr17a45:
   set(§§pop(),§§pop());
   set("",40);
   set("","O{invalid_utf8=150}\x02");
   set("\b\n\x1c{invalid_utf8=150}\n",20);
   §§goto(addr17bae);
   §§goto(addr17bad);
}
